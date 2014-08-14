"""This module does the actual generation of the QR codes. The QRCodeBuilder
builds the code. While the various output methods draw the code into a file.
"""

#Imports required for 2.7 support
from __future__ import absolute_import, division, print_function, with_statement, unicode_literals

import pyqrcode.tables as tables
import io
import sys
import itertools

class QRCodeBuilder:
    """This class generates a QR code based on the standard. It is meant to
    be used internally, not by users!!!

    This class implements the tutorials found at:

    * http://www.thonky.com/qr-code-tutorial/

    * http://www.matchadesign.com/blog/qr-code-demystified-part-6/

    This class also uses the standard, which can be read online at:
        http://raidenii.net/files/datasheets/misc/qr_code.pdf

    Test codes were tested against:
        http://zxing.org/w/decode.jspx

    Also, reference codes were generated at:
        http://www.morovia.com/free-online-barcode-generator/qrcode-maker.php

    QR code Debugger:
        http://qrlogo.kaarposoft.dk/qrdecode.html
    """
    def __init__(self, data, version, mode, error):
        """See :py:class:`pyqrcode.QRCode` for information on the parameters."""

        #Set what data we are going to use to generate
        #the QR code
        if isinstance(data, bytes):
            self.data = data.decode('utf-8')
        else:
            self.data = data

        #Check that the user passed in a valid mode
        if mode in tables.modes.keys():
            self.mode = tables.modes[mode]
        else:
            raise LookupError('{} is not a valid mode.'.format(mode))

        #Check that the user passed in a valid error level
        if error in tables.error_level.keys():
            self.error = tables.error_level[error]
        else:
            raise LookupError('{} is not a valid error '
                                'level.'.format(error))

        if 1 <= version <= 40:
            self.version = version
        else:
            raise ValueError("The version must between 1 and 40.")

        #Look up the proper row for error correction code words
        self.error_code_words = tables.eccwbi[version][self.error]

        #This property will hold the binary string as it is built
        self.buffer = io.StringIO()

        #Create the binary data block
        self.add_data()

        #Create the actual QR code
        self.make_code()

    def grouper(self, n, iterable, fillvalue=None):
        """This generator yields a set of tuples, where the
        iterable is broken into n sized chunks. If the
        iterable is not evenly sized then fillvalue will
        be appended to the last tuple to make up the difference.

        This function is copied from the standard docs on
        itertools.
        """
        args = [iter(iterable)] * n
        if hasattr(itertools, 'zip_longest'):
            return itertools.zip_longest(*args, fillvalue=fillvalue)
        return itertools.izip_longest(*args, fillvalue=fillvalue)

    def binary_string(self, data, length):
        """This method returns a string of length n that is the binary
        representation of the given data. This function is used to
        basically create bit fields of a given size.
        """
        return '{{:0{}b}}'.format(length).format(int(data))

    def get_data_length(self):
        """QR codes contain a "data length" field. This method creates this
        field. A binary string representing the appropriate length is
        returned.
        """

        #The "data length" field varies by the type of code and its mode.
        #discover how long the "data length" field should be.
        if 1 <= self.version <= 9:
            max_version = 9
        elif 10 <= self.version <= 26:
            max_version = 26
        elif 27 <= self.version <= 40:
            max_version = 40

        data_length = tables.data_length_field[max_version][self.mode]

        length_string = self.binary_string(len(self.data), data_length)

        if len(length_string) > data_length:
            raise ValueError('The supplied data will not fit '
                               'within this version of a QRCode.')
        return length_string

    def encode(self):
        """This method encodes the data into a binary string using
        the appropriate algorithm specified by the mode.
        """
        if self.mode == tables.modes['alphanumeric']:
            encoded = self.encode_alphanumeric()
        elif self.mode == tables.modes['numeric']:
            encoded = self.encode_numeric()
        elif self.mode == tables.modes['bytes']:
            encoded = self.encode_bytes()
        else:
            raise ValueError('This mode is not yet implemented.')

        bits = self.terminate_bits(encoded)
        if bits is not None:
            encoded += bits

        return encoded

    def encode_alphanumeric(self):
        """This method encodes the QR code's data if its mode is
        alphanumeric. It returns the data encoded as a binary string.
        """
        #Convert the string to upper case
        self.data = self.data.upper()

        #Change the data such that it uses a QR code ascii table
        ascii = []
        for char in self.data:
            ascii.append(tables.ascii_codes[char])

        #Now perform the algorithm that will make the ascii into bit fields
        with io.StringIO() as buf:
            for (a,b) in self.grouper(2, ascii):
                if b is not None:
                    buf.write(self.binary_string((45*a)+b, 11))
                else:
                    #This occurs when there is an odd number
                    #of characters in the data
                    buf.write(self.binary_string(a, 6))

            #Return the binary string
            return buf.getvalue()

    def encode_numeric(self):
        """This method encodes the QR code's data if its mode is
        numeric. It returns the data encoded as a binary string.
        """
        with io.StringIO() as buf:
            #Break the number into groups of three digits
            for triplet in self.grouper(3, self.data):
                number = ''
                for digit in triplet:
                    #Only build the string if digit is not None
                    if digit:
                        number = ''.join([number, digit])
                    else:
                        break

                #If the number is one digits, make a 4 bit field
                if len(number) == 1:
                    bin = self.binary_string(number, 4)

                #If the number is two digits, make a 7 bit field
                elif len(number) == 2:
                    bin = self.binary_string(number, 7)

                #Three digit numbers use a 10 bit field
                else:
                    bin = self.binary_string(number, 10)

                buf.write(bin)
            return buf.getvalue()

    def encode_bytes(self):
        """This method encodes the QR code's data if its mode is
        8 bit mode. It returns the data encoded as a binary string.
        """
        with io.StringIO() as buf:
            for char in self.data.encode('ascii'):
                if isinstance(char, int):
                    buf.write('{{:0{}b}}'.format(8).format(char))
                if isinstance(char, str):
                    buf.write('{{:0{}b}}'.format(8).format(ord(char)))
            return buf.getvalue()


    def add_data(self):
        """This function properly constructs a QR code's data string. It takes
        into account the interleaving pattern required by the standard.
        """
        #Encode the data into a QR code
        self.buffer.write(self.binary_string(self.mode, 4))
        self.buffer.write(self.get_data_length())
        self.buffer.write(self.encode())

        #delimit_words and add_words can return None
        add_bits = self.delimit_words()
        if add_bits:
            self.buffer.write(add_bits)

        fill_bytes = self.add_words()
        if fill_bytes:
            self.buffer.write(fill_bytes)

        #Get a numeric representation of the data
        data = [int(''.join(x),2)
                    for x in self.grouper(8, self.buffer.getvalue())]

        #This is the error information for the code
        error_info = tables.eccwbi[self.version][self.error]

        #This will hold our data blocks
        data_blocks = []

        #This will hold our error blocks
        error_blocks = []

        #Some codes have the data sliced into two different sized blocks
        #for example, first two 14 word sized blocks, then four 15 word
        #sized blocks. This means that slicing size can change over time.
        data_block_sizes = [error_info[2]] * error_info[1]
        if error_info[3] != 0:
            data_block_sizes.extend([error_info[4]] * error_info[3])

        #For every block of data, slice the data into the appropriate
        #sized block
        current_byte = 0
        for n_data_blocks in data_block_sizes:
            data_blocks.append(data[current_byte:current_byte+n_data_blocks])
            current_byte += n_data_blocks

        if current_byte < len(data):
            raise ValueError('Too much data for this code version.')

        #DEBUG CODE!!!!
        #Print out the data blocks
        #print('Data Blocks:\n{}'.format(data_blocks))

        #Calculate the error blocks
        for n, block in enumerate(data_blocks):
            error_blocks.append(self.make_error_block(block, n))

        #DEBUG CODE!!!!
        #Print out the error blocks
        #print('Error Blocks:\n{}'.format(error_blocks))

        #Buffer we will write our data blocks into
        data_buffer = io.StringIO()

        #Add the data blocks
        #Write the buffer such that: block 1 byte 1, block 2 byte 1, etc.
        largest_block = max(error_info[2], error_info[4])+error_info[0]
        for i in range(largest_block):
            for block in data_blocks:
                if i < len(block):
                    data_buffer.write(self.binary_string(block[i], 8))

        #Add the error code blocks.
        #Write the buffer such that: block 1 byte 1, block 2 byte 2, etc.
        for i in range(error_info[0]):
            for block in error_blocks:
                data_buffer.write(self.binary_string(block[i], 8))

        self.buffer = data_buffer

    def terminate_bits(self, payload):
        """This method adds zeros to the end of the encoded data so that the
        encoded data is of the correct length. It returns a binary string
        containing the bits to be added.
        """
        data_capacity = tables.data_capacity[self.version][self.error][0]

        if len(payload) > data_capacity:
            raise ValueError('The supplied data will not fit '
                             'within this version of a QR code.')

        #We must add up to 4 zeros to make up for any shortfall in the
        #length of the data field.
        if len(payload) == data_capacity:
            return None
        elif len(payload) <= data_capacity-4:
            bits = self.binary_string(0,4)
        else:
            #Make up any shortfall need with less than 4 zeros
            bits = self.binary_string(0, data_capacity - len(payload))

        return bits

    def delimit_words(self):
        """This method takes the existing encoded binary string
        and returns a binary string that will pad it such that
        the encoded string contains only full bytes.
        """
        bits_short = 8 - (len(self.buffer.getvalue()) % 8)

        #The string already falls on an byte boundary do nothing
        if bits_short == 8:
            return None
        else:
            return self.binary_string(0, bits_short)

    def add_words(self):
        """The data block must fill the entire data capacity of the QR code.
        If we fall short, then we must add bytes to the end of the encoded
        data field. The value of these bytes are specified in the standard.
        """

        data_blocks = len(self.buffer.getvalue()) // 8
        total_blocks = tables.data_capacity[self.version][self.error][0] // 8
        needed_blocks = total_blocks - data_blocks

        if needed_blocks == 0:
            return None

        #This will return item1, item2, item1, item2, etc.
        block = itertools.cycle(['11101100', '00010001'])

        #Create a string of the needed blocks
        return ''.join([next(block) for x in range(needed_blocks)])

    def _fix_exp(self, exponent):
        """Makes sure the exponent ranges from 0 to 255."""
        #return (exponent % 256) + (exponent // 256)
        return exponent % 255

    def make_error_block(self, block, block_number):
        """This function constructs the error correction block of the
        given data block. This is *very complicated* process. To
        understand the code you need to read:

        * http://www.thonky.com/qr-code-tutorial/part-2-error-correction/
        * http://www.matchadesign.com/blog/qr-code-demystified-part-4/
        """
        #Get the error information from the standards table
        error_info = tables.eccwbi[self.version][self.error]

        #This is the number of 8-bit words per block
        if block_number < error_info[1]:
            code_words_per_block = error_info[2]
        else:
            code_words_per_block = error_info[4]

        #This is the size of the error block
        error_block_size = error_info[0]

        #Copy the block as the message polynomial coefficients
        mp_co = block[:]

        #Add the error blocks to the message polynomial
        mp_co.extend([0] * (error_block_size))

        #Get the generator polynomial
        generator = tables.generator_polynomials[error_block_size]

        #This will hold the temporary sum of the message coefficient and the
        #generator polynomial
        gen_result = [0] * len(generator)

        #Go through every code word in the block
        for i in range(code_words_per_block):
            #Get the first coefficient from the message polynomial
            coefficient = mp_co.pop(0)

            #Skip coefficients that are zero
            if coefficient == 0:
                continue
            else:
                #Turn the coefficient into an alpha exponent
                alpha_exp = tables.galois_antilog[coefficient]

            #Add the alpha to the generator polynomial
            for n in range(len(generator)):
                gen_result[n] = alpha_exp + generator[n]
                if gen_result[n] > 255:
                    gen_result[n] = gen_result[n] % 255

                #Convert the alpha notation back into coefficients
                gen_result[n] = tables.galois_log[gen_result[n]]

                #XOR the sum with the message coefficients
                mp_co[n] = gen_result[n] ^ mp_co[n]

        #Pad the end of the error blocks with zeros if needed
        if len(mp_co) < code_words_per_block:
            mp_co.extend([0] * (code_words_per_block - len(mp_co)))

        return mp_co

    def make_code(self):
        """This method returns the best possible QR code."""
        from copy import deepcopy

        #Get the size of the underlying matrix
        matrix_size = tables.version_size[self.version]

        #Create a template matrix we will build the codes with
        row = [' ' for x in range(matrix_size)]
        template = [deepcopy(row) for x in range(matrix_size)]

        #Add mandatory information to the template
        self.add_detection_pattern(template)
        self.add_position_pattern(template)
        self.add_version_pattern(template)

        #Create the various types of masks of the template
        self.masks = self.make_masks(template)

        self.best_mask = self.choose_best_mask()
        self.code = self.masks[self.best_mask]

    def add_detection_pattern(self, m):
        """This method add the detection patterns to the QR code. This lets
        the scanner orient the pattern. It is required for all QR codes.
        The detection pattern consists of three boxes located at the upper
        left, upper right, and lower left corners of the matrix. Also, two
        special lines called the timing pattern is also necessary. Finally,
        a single black pixel is added just above the lower left black box.
        """

        #Draw outer black box
        for i in range(7):
            inv = -(i+1)
            for j in [0,6,-1,-7]:
                m[j][i] = 1
                m[i][j] = 1
                m[inv][j] = 1
                m[j][inv] = 1

        #Draw inner white box
        for i in range(1, 6):
            inv = -(i+1)
            for j in [1, 5, -2, -6]:
                m[j][i] = 0
                m[i][j] = 0
                m[inv][j] = 0
                m[j][inv] = 0

        #Draw inner black box
        for i in range(2, 5):
            for j in range(2, 5):
                inv = -(i+1)
                m[i][j] = 1
                m[inv][j] = 1
                m[j][inv] = 1

        #Draw white border
        for i in range(8):
            inv = -(i+1)
            for j in [7, -8]:
                m[i][j] = 0
                m[j][i] = 0
                m[inv][j] = 0
                m[j][inv] = 0

        #To keep the code short, it draws an extra box
        #in the lower right corner, this removes it.
        for i in range(-8, 0):
            for j in range(-8, 0):
                m[i][j] = ' '

        #Add the timing pattern
        bit = itertools.cycle([1,0])
        for i in range(8, (len(m)-8)):
            b = next(bit)
            m[i][6] = b
            m[6][i] = b

        #Add the extra black pixel
        m[-8][8] = 1

    def add_position_pattern(self, m):
        """This method draws the position adjustment patterns onto the QR
        Code. All QR code versions larger than one require these special boxes
        called position adjustment patterns.
        """
        #Version 1 does not have a position adjustment pattern
        if self.version == 1:
            return

        #Get the coordinates for where to place the boxes
        coordinates = tables.position_adjustment[self.version]

        #Get the max and min coordinates to handle special cases
        min_coord = coordinates[0]
        max_coord = coordinates[-1]

        #Draw a box at each intersection of the coordinates
        for i in coordinates:
            for j in coordinates:
                #Do not draw these boxes because they would
                #interfere with the detection pattern
                if (i == min_coord and j == min_coord) or \
                   (i == min_coord and j == max_coord) or \
                   (i == max_coord and j == min_coord):
                    continue

                #Center black pixel
                m[i][j] = 1

                #Surround the pixel with a white box
                for x in [-1,1]:
                    m[i+x][j+x] = 0
                    m[i+x][j] = 0
                    m[i][j+x] = 0
                    m[i-x][j+x] = 0
                    m[i+x][j-x] = 0

                #Surround the white box with a black box
                for x in [-2,2]:
                    for y in [0,-1,1]:
                        m[i+x][j+x] = 1
                        m[i+x][j+y] = 1
                        m[i+y][j+x] = 1
                        m[i-x][j+x] = 1
                        m[i+x][j-x] = 1

    def add_version_pattern(self, m):
        """For QR codes with a version 7 or higher, a special pattern
        specifying the code's version is required.

        For further information see:
        http://www.thonky.com/qr-code-tutorial/format-version-information/#example-of-version-7-information-string
        """
        if self.version < 7:
            return

        #Get the bit fields for this code's version
        #We will iterate across the string, the bit string
        #needs the least significant digit in the zero-th position
        field = iter(tables.version_pattern[self.version][::-1])

        #Where to start placing the pattern
        start = len(m)-11

        #The version pattern is pretty odd looking
        for i in range(6):
            #The pattern is three modules wide
            for j in range(start, start+3):
                bit = int(next(field))

                #Bottom Left
                m[i][j] = bit

                #Upper right
                m[j][i] = bit

    def make_masks(self, template):
        """This method generates all seven masks so that the best mask can
        be determined. The template parameter is a code matrix that will
        server as the base for all the generated masks.
        """
        from copy import deepcopy

        nmasks = len(tables.mask_patterns)
        masks = [''] * nmasks
        count = 0

        for n in range(nmasks):
            cur_mask = deepcopy(template)
            masks[n] = cur_mask

            #Add the type pattern bits to the code
            self.add_type_pattern(cur_mask, tables.type_bits[self.error][n])

            #Get the mask pattern
            pattern = tables.mask_patterns[n]

            #This will read the 1's and 0's one at a time
            bits = iter(self.buffer.getvalue())

            #These will help us do the up, down, up, down pattern
            row_start = itertools.cycle([len(cur_mask)-1, 0])
            row_stop = itertools.cycle([-1,len(cur_mask)])
            direction = itertools.cycle([-1, 1])

            #The data pattern is added using pairs of columns
            for column in range(len(cur_mask)-1, 0, -2):

                #The vertical timing pattern is an exception to the rules,
                #move the column counter over by one
                if column <= 6:
                    column = column - 1

                #This will let us fill in the pattern
                #right-left, right-left, etc.
                column_pair = itertools.cycle([column, column-1])

                #Go through each row in the pattern moving up, then down
                for row in range(next(row_start), next(row_stop),
                                 next(direction)):

                    #Fill in the right then left column
                    for i in range(2):
                        col = next(column_pair)

                        #Go to the next column if we encounter a
                        #preexisting pattern (usually an alignment pattern)
                        if cur_mask[row][col] != ' ':
                            continue

                        #Some versions don't have enough bits. You then fill
                        #in the rest of the pattern with 0's. These are
                        #called "remainder bits."
                        try:
                            bit = int(next(bits))
                        except:
                            bit = 0


                        #If the pattern is True then flip the bit
                        if pattern(row, col):
                            cur_mask[row][col] = bit ^ 1
                        else:
                            cur_mask[row][col] = bit

        #DEBUG CODE!!!
        #Save all of the masks as png files
        #for i, m in enumerate(masks):
        #    _png(m, self.version, 'mask-{}.png'.format(i), 5)

        return masks

    def choose_best_mask(self):
        """This method returns the index of the "best" mask as defined by
        having the lowest total penalty score. The penalty rules are defined
        by the standard. The mask with the lowest total score should be the
        easiest to read by optical scanners.
        """
        self.scores = []
        for n in range(len(self.masks)):
            self.scores.append([0,0,0,0])

        #Score penalty rule number 1
        #Look for five consecutive squares with the same color.
        #Each one found gets a penalty of 3 + 1 for every
        #same color square after the first five in the row.
        for (n, mask) in enumerate(self.masks):
            current = mask[0][0]
            counter = 0
            total = 0

            #Examine the mask row wise
            for row in range(0,len(mask)):
                counter = 0
                for col  in range(0,len(mask)):
                    bit = mask[row][col]

                    if bit == current:
                        counter += 1
                    else:
                        if counter >= 5:
                            total += (counter - 5) + 3
                        counter = 1
                        current = bit
                if counter >= 5:
                    total += (counter - 5) + 3

            #Examine the mask column wise
            for col in range(0,len(mask)):
                counter = 0
                for row in range(0,len(mask)):
                    bit = mask[row][col]

                    if bit == current:
                        counter += 1
                    else:
                        if counter >= 5:
                            total += (counter - 5) + 3
                        counter = 1
                        current = bit
                if counter >= 5:
                    total += (counter - 5) + 3

            self.scores[n][0] = total

        #Score penalty rule 2
        #This rule will add 3 to the score for each 2x2 block of the same
        #colored pixels there are.
        for (n, mask) in enumerate(self.masks):
            count = 0
            #Don't examine the 0th and Nth row/column
            for i in range(0, len(mask)-1):
                for j in range(0, len(mask)-1):
                    if mask[i][j] == mask[i+1][j]   and \
                       mask[i][j] == mask[i][j+1]   and \
                       mask[i][j] == mask[i+1][j+1]:
                        count += 1

            self.scores[n][1] = count * 3

        #Score penalty rule 3
        #This rule looks for 1011101 within the mask prefixed
        #and/or suffixed by four zeros.
        patterns = [[0,0,0,0,1,0,1,1,1,0,1],
                    [1,0,1,1,1,0,1,0,0,0,0],]
                    #[0,0,0,0,1,0,1,1,1,0,1,0,0,0,0]]

        for (n, mask) in enumerate(self.masks):
            nmatches = 0

            for i in range(len(mask)):
                for j in range(len(mask)):
                    for pattern in patterns:
                        match = True
                        k = j
                        #Look for row matches
                        for p in pattern:
                            if k >= len(mask) or mask[i][k] != p:
                                match = False
                                break
                            k += 1
                        if match:
                            nmatches += 1

                        match = True
                        k = j
                        #Look for column matches
                        for p in pattern:
                            if k >= len(mask) or mask[k][i] != p:
                                match = False
                                break
                            k += 1
                        if match:
                            nmatches += 1


            self.scores[n][2] = nmatches * 40

        #Score the last rule, penalty rule 4. This rule measures how close
        #the pattern is to being 50% black. The further it deviates from
        #this this ideal the higher the penalty.
        for (n, mask) in enumerate(self.masks):
            nblack = 0
            for row in mask:
                nblack += sum(row)

            total_pixels = len(mask)**2
            ratio = nblack / total_pixels
            percent = (ratio * 100) - 50
            self.scores[n][3] = int((abs(int(percent)) / 5) * 10)


        #Calculate the total for each score
        totals = [0] * len(self.scores)
        for i in range(len(self.scores)):
            for j in range(len(self.scores[i])):
                totals[i] +=  self.scores[i][j]

        #DEBUG CODE!!!
        #Prints out a table of scores
        #print('Rule Scores\n      1     2     3     4    Total')
        #for i in range(len(self.scores)):
        #    print(i, end='')
        #    for s in self.scores[i]:
        #        print('{: >6}'.format(s), end='')
        #    print('{: >7}'.format(totals[i]))
        #print('Mask Chosen: {}'.format(totals.index(min(totals))))

        #The lowest total wins
        return totals.index(min(totals))

    def add_type_pattern(self, m, type_bits):
        """This will add the pattern to the QR code that represents the error
        level and the type of mask used to make the code.
        """
        field = iter(type_bits)
        for i in range(7):
            bit = int(next(field))

            #Skip the timing bits
            if i < 6:
                m[8][i] = bit
            else:
                m[8][i+1] = bit

            if -8 < -(i+1):
                m[-(i+1)][8] = bit

        for i in range(-8,0):
            bit = int(next(field))

            m[8][i] = bit

            i = -i
            #Skip timing column
            if i > 6:
                m[i][8] = bit
            else:
                m[i-1][8] = bit

##############################################################################
##############################################################################
#
# Output Functions
#
##############################################################################
##############################################################################

def _get_file(file, mode):
    """This method returns the file parameter if it is an open writable
    stream. Otherwise it treats the file parameter as a file path and
    opens it with the given mode. It is used by the svg and png methods
    to interpret the file parameter.
    """
    import os.path
    #See if the file parameter is a stream
    if not isinstance(file, io.IOBase):
        #If it is not a stream open a the file path
        return open(os.path.abspath(file), mode)
    elif not file.writable():
        raise ValueError('Stream is not writable.')
    else:
        return file

def _get_png_size(version, scale):
    """See: QRCode.get_png_size

    This function was abstracted away from QRCode to allow for the output of
    QR codes during the build process, i.e. for debugging. It works
    just the same except you must specify the code's version. This is needed
    to calculate the PNG's size.
    """
    #Formula: scale times number of modules plus the border on each side
    return (scale * tables.version_size[version]) + (2 * scale)

def _text(code):
    """This method returns a text based representation of the QR code.
    This is useful for debugging purposes.
    """
    buf = io.StringIO()

    border_row = '0' * (len(code[0]) + 2)

    buf.write(border_row)
    buf.write('\n')
    for row in code:
        buf.write('0')
        for bit in row:
            if bit == 1:
                buf.write('1')
            elif bit == 0:
                buf.write('0')
            #This is for debugging unfinished QR codes,
            #unset pixels will be spaces.
            else:
                buf.write(' ')
        buf.write('0\n')

    buf.write(border_row)

    return buf.getvalue()

def _svg(code, version, file, scale=1, module_color='black', background=None):
    """This method writes the QR code out as an SVG document. The
    code is drawn by drawing only the modules corresponding to a 1. They
    are drawn using a line, such that contiguous modules in a row
    are drawn with a single line. The file parameter is used to
    specify where to write the document to. It can either be an writable
    stream or a file path. The scale parameter is sets how large to draw
    a single module. By default one pixel is used to draw a single
    module. This may make the code to small to be read efficiently.
    Increasing the scale will make the code larger. This method will accept
    fractional scales (e.g. 2.5).
    """
    #This is the template for the svg line. It is placed here so it
    #does not need to be recreated for each call to line().
    line_template = '''
        <line class="pyqrline" x1="{}" y1="{}" x2="{}" y2="{}"
              stroke="{}" stroke-width="{}"/>'''

    def line(x1, y1, x2, y2, color):
        """This sub-function draws the modules. It attempts to draw them
        as a single line per row, rather than as individual rectangles.
        It uses the l variable as a template t
        """
        return line_template.format(x1+scale, y1+scale, x2+scale, y2+scale,
                                    color, scale)

    file = _get_file(file, 'w')

    #Write the document header
    file.write("""<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
           "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

        <svg xmlns="http://www.w3.org/2000/svg" class="pyqrcode"
             width="{0}" height="{0}">
        <title>QR code</title>
        """.format((tables.version_size[version]*scale)+(2*scale)))

    #Draw a background rectangle if necessary
    if background:
        file.write("""
            <rect width="{0}" height="{0}" style="fill:{1};stroke-width:0" />
            """.format((tables.version_size[version]*scale)+(2*scale),
                       background))

    #This will hold the current row number
    rnumber = 0

    #The current "color," used to define starting a line and ending a line.
    color = 'black'

    #Loop through each row of the code
    for row in code:
        colnumber = 0       #Reset column number
        start_column = 0    #Reset the starting_column number

        #Examine every bit in the row
        for bit in row:
            #Set the color of the bit
            if bit == 1:
                new_color = 'black'
            elif bit == 0:
                new_color = 'white'

            #DEBUG CODE!!
            #In unfinished QR codes, unset pixels will be red
            #else:
                #new_color = 'red'

            #When the color changes then draw a line
            if new_color != color:
                #Don't draw the white background
                if color != 'white':
                    file.write(line(start_column, rnumber,
                                    colnumber, rnumber, color))

                #Move the next line's starting color and number
                start_column = colnumber
                color = new_color

            #Accumulate the column
            colnumber += scale

        #End the row by drawing out the accumulated line
        #if it is not the background
        if color != 'white':
            file.write(line(start_column, rnumber,
                            colnumber, rnumber, color))

        #Set row number
        rnumber += scale


    #Close the document
    file.write("</svg>\n")

def _png(code, version, file, scale=1, module_color=None, background=None):
    """See: pyqrcode.QRCode.png()

    This function was abstracted away from QRCode to allow for the output of
    QR codes during the build process, i.e. for debugging. It works
    just the same except you must specify the code's version. This is needed
    to calculate the PNG's size.

    This method will write the given file out as a PNG file. Note, it
    depends on the PyPNG module to do this.
    """
    import png

    #Coerce scale parameter into an integer
    try:
        scale = int(scale)
    except ValueError:
        raise ValueError('The scale parameter must be an integer')

    def scale_code(code):
        """To perform the scaling we need to inflate the number of bits.
        The PNG library expects all of the bits when it draws the PNG.
        Effectively, we double, tripple, etc. the number of columns and
        the number of rows.
        """
        #This is the row to show up at the top and bottom border
        border_module = [1] * scale
        border_row = [1] * _get_png_size(version, scale)
        border = [border_row] * scale


        #This is one row's worth of each possible module
        #PNG's use 0 for black and 1 for white, this is the
        #reverse of the QR standard
        black = [0] * scale
        white = [1] * scale

        #This will hold the final PNG's bits
        bits = []

        #Add scale rows before the code as a border,
        #as per the standard
        bits.extend(border)

        #Add each row of the to the final PNG bits
        for row in code:
            tmp_row = []

            #Add one all white module to the beginning
            #to create the vertical border
            tmp_row.extend(border_module)

            #Go through each bit in the code
            for item in row:
                #Add one scaled module
                if item == 0:
                    tmp_row.extend(white)
                else:
                    tmp_row.extend(black)

            #Add one all white module to the end
            #to create the vertical border
            tmp_row.extend(border_module)

            #Copy each row scale times
            for n in range(scale):
                bits.append(tmp_row)

        #Add the bottom border
        bits.extend(border)

        return bits

    def png_pallete_color(color):
        """This creates a palette color from a list or tuple. The list or
        tuple must be of length 3 (for rgb) or 4 (for rgba). The values
        must be between 0 and 255. Note rgb colors will be given an added
        alpha component set to 255.

        The pallete color is represented as a list, this is what is returned.
        """
        if color:
            rgba = []
            if not (3 <= len(color) <= 4):
                raise ValueError('Colors must be a list or tuple of length '
                                 ' 3 or 4. You passed in '
                                 '"{}".'.format(color))

            for c in color:
                c = int(c)
                if 0 <= c <= 255:
                    rgba.append(int(c))
                else:
                    raise ValueError('Color components must be between '
                                     ' 0 and 255')

            #Make all all colors have an alpha channel
            if len(rgba) == 3:
                rgba.append(255)

        return rgba

    #If the user passes in one parameter, then they must pass in both or neither
    #Note, this is a logical xor
    if (not module_color) != (not background):
        raise ValueError('If you specify either the black or white parameter, '
                         'then you must specify both.')

    #Create the pallete, or set greyscale to True
    if module_color:
        palette = [png_pallete_color(module_color),
                   png_pallete_color(background)]
        greyscale = False
    else:
        palette = None
        greyscale = True

    #The size of the PNG
    size = _get_png_size(version, scale)

    #We need to increase the size of the code to match up to the
    #scale parameter.
    code = scale_code(code)

    #Write out the PNG
    with _get_file(file, 'wb') as f:
        w = png.Writer(width=size, height=size, greyscale=greyscale,
                       palette=palette, bitdepth=1)

        w.write(f, code)
