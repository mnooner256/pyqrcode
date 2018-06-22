# -*- coding: utf-8 -*-
# Copyright (c) 2013, Michael Nooner
# Copyright (c) 2018, Lars Heuer
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its 
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""This module does the actual generation of the QR codes. The QRCodeBuilder
builds the code. While the various output methods draw the code into a file.

This module does not belong to the public API.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import pyqrcode.tables as tables
import io
import itertools
try:  # pragma: no cover
    from itertools import zip_longest
except ImportError:  # pragma: no cover
    # Py2
    from itertools import izip_longest as zip_longest
    range = xrange
    str = unicode

# <https://wiki.python.org/moin/PortingToPy3k/BilingualQuickRef#New_Style_Classes>
__metaclass__ = type


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

    Also, reference codes were generat/ed at:
        http://www.morovia.com/free-online-barcode-generator/qrcode-maker.php
        http://demos.telerik.com/aspnet-ajax/barcode/examples/qrcode/defaultcs.aspx

    QR code Debugger:
        http://qrlogo.kaarposoft.dk/qrdecode.html
    """
    def __init__(self, data, version, mode, error):
        """See :py:class:`pyqrcode.QRCode` for information on the parameters."""
        #Set what data we are going to use to generate
        #the QR code
        self.data = data

        #Check that the user passed in a valid mode
        if mode in tables.modes:
            self.mode = tables.modes[mode]
        else:
            raise ValueError('{0} is not a valid mode.'.format(mode))

        #Check that the user passed in a valid error level
        if error in tables.error_level:
            self.error = tables.error_level[error]
        else:
            raise ValueError('{0} is not a valid error '
                             'level.'.format(error))

        if 1 <= version <= 40:
            self.version = version
        else:
            raise ValueError("Illegal version {0}, version must be between "
                             "1 and 40.".format(version))

        #Look up the proper row for error correction code words
        self.error_code_words = tables.eccwbi[version][self.error]

        #This property will hold the binary string as it is built
        self.buffer = io.StringIO()

        #Create the binary data block
        self.add_data()

        #Create the actual QR code
        self.make_code()

    @staticmethod
    def grouper(n, iterable, fillvalue=None):
        """This generator yields a set of tuples, where the
        iterable is broken into n sized chunks. If the
        iterable is not evenly sized then fillvalue will
        be appended to the last tuple to make up the difference.

        This function is copied from the standard docs on
        itertools.
        """
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    @staticmethod
    def binary_string(data, length):
        """This method returns a string of length n that is the binary
        representation of the given data. This function is used to
        basically create bit fields of a given size.
        """
        return '{{0:0{0}b}}'.format(length).format(int(data))

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

        if self.mode != tables.modes['kanji']:
            length_string = QRCodeBuilder.binary_string(len(self.data), data_length)
        else:
            length_string = QRCodeBuilder.binary_string(len(self.data) / 2, data_length)

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
        elif self.mode == tables.modes['binary']:
            encoded = self.encode_bytes()
        elif self.mode == tables.modes['kanji']:
            encoded = self.encode_kanji()
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
            if isinstance(char, int):
                ascii.append(tables.ascii_codes[chr(char)])
            else:
                ascii.append(tables.ascii_codes[char])
        
        #Now perform the algorithm that will make the ascii into bit fields
        with io.StringIO() as buf:
            for (a,b) in QRCodeBuilder.grouper(2, ascii):
                if b is not None:
                    buf.write(QRCodeBuilder.binary_string((45*a)+b, 11))
                else:
                    #This occurs when there is an odd number
                    #of characters in the data
                    buf.write(QRCodeBuilder.binary_string(a, 6))

            #Return the binary string
            return buf.getvalue()

    def encode_numeric(self):
        """This method encodes the QR code's data if its mode is
        numeric. It returns the data encoded as a binary string.
        """
        with io.StringIO() as buf:
            #Break the number into groups of three digits
            for triplet in QRCodeBuilder.grouper(3, self.data):
                number = ''
                for digit in triplet:
                    if isinstance(digit, int):
                        digit = chr(digit)

                    #Only build the string if digit is not None
                    if digit:
                        number = ''.join([number, digit])
                    else:
                        break

                #If the number is one digits, make a 4 bit field
                if len(number) == 1:
                    bin = QRCodeBuilder.binary_string(number, 4)
                elif len(number) == 2:  # If the number is two digits, make a 7 bit field
                    bin = QRCodeBuilder.binary_string(number, 7)
                else:  # Three digit numbers use a 10 bit field
                    bin = QRCodeBuilder.binary_string(number, 10)

                buf.write(bin)
            return buf.getvalue()

    def encode_bytes(self):
        """This method encodes the QR code's data if its mode is
        8 bit mode. It returns the data encoded as a binary string.
        """
        with io.StringIO() as buf:
            for char in self.data:
                if not isinstance(char, int):
                    buf.write('{{0:0{0}b}}'.format(8).format(ord(char)))
                else:
                    buf.write('{{0:0{0}b}}'.format(8).format(char))
            return buf.getvalue()

    def encode_kanji(self):
        """This method encodes the QR code's data if its mode is
        kanji. It returns the data encoded as a binary string.
        """
        def two_bytes(data):
            """Output two byte character code as a single integer."""
            def next_byte(b):
                """Make sure that character code is an int. Python 2 and
                3 compatibility.
                """
                if not isinstance(b, int):
                    return ord(b)
                else:
                    return b

            #Go through the data by looping to every other character
            for i in range(0, len(data), 2):
                yield (next_byte(data[i]) << 8) | next_byte(data[i+1])

        #Force the data into Kanji encoded bytes
        if isinstance(self.data, bytes):
            data = self.data.decode('shiftjis').encode('shiftjis')
        else:
            data = self.data.encode('shiftjis')
        
        #Now perform the algorithm that will make the kanji into 13 bit fields
        with io.StringIO() as buf:
            for asint in two_bytes(data):
                #Shift the two byte value as indicated by the standard
                if 0x8140 <= asint <= 0x9FFC:
                    difference = asint - 0x8140
                elif 0xE040 <= asint <= 0xEBBF:
                    difference = asint - 0xC140

                #Split the new value into most and least significant bytes
                msb = (difference >> 8)
                lsb = (difference & 0x00FF)

                #Calculate the actual 13 bit binary value
                buf.write('{0:013b}'.format((msb * 0xC0) + lsb))
            #Return the binary string
            return buf.getvalue()

    def add_data(self):
        """This function properly constructs a QR code's data string. It takes
        into account the interleaving pattern required by the standard.
        """
        #Encode the data into a QR code
        self.buffer.write(QRCodeBuilder.binary_string(self.mode, 4))
        self.buffer.write(self.get_data_length())
        self.buffer.write(self.encode())

        #Converts the buffer into "code word" integers.
        #The online debugger outputs them this way, makes
        #for easier comparisons.
        #s = self.buffer.getvalue()
        #for i in range(0, len(s), 8):
        #    print(int(s[i:i+8], 2), end=',')
        #print()
        
        #Fix for issue #3: https://github.com/mnooner256/pyqrcode/issues/3#
        #I was performing the terminate_bits() part in the encoding.
        #As per the standard, terminating bits are only supposed to
        #be added after the bit stream is complete. I took that to
        #mean after the encoding, but actually it is after the entire
        #bit stream has been constructed.
        bits = self.terminate_bits(self.buffer.getvalue())
        if bits is not None:
            self.buffer.write(bits)

        #delimit_words and add_words can return None
        add_bits = self.delimit_words()
        if add_bits:
            self.buffer.write(add_bits)
        
        fill_bytes = self.add_words()
        if fill_bytes:
            self.buffer.write(fill_bytes)
        
        #Get a numeric representation of the data
        data = [int(''.join(x),2)
                    for x in QRCodeBuilder.grouper(8, self.buffer.getvalue())]

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
        
        #I am not sure about the test after the "and". This was added to
        #fix a bug where after delimit_words padded the bit stream, a zero
        #byte ends up being added. After checking around, it seems this extra
        #byte is supposed to be chopped off, but I cannot find that in the
        #standard! I am adding it to solve the bug, I believe it is correct.
        if current_byte < len(data):
            raise ValueError('Too much data for this code version.')

        #DEBUG CODE!!!!
        #Print out the data blocks
        #print('Data Blocks:\n{0}'.format(data_blocks))

        #Calculate the error blocks
        for n, block in enumerate(data_blocks):
            error_blocks.append(self.make_error_block(block, n))

        #DEBUG CODE!!!!
        #Print out the error blocks
        #print('Error Blocks:\n{0}'.format(error_blocks))

        #Buffer we will write our data blocks into
        data_buffer = io.StringIO()

        #Add the data blocks
        #Write the buffer such that: block 1 byte 1, block 2 byte 1, etc.
        largest_block = max(error_info[2], error_info[4])+error_info[0]
        for i in range(largest_block):
            for block in data_blocks:
                if i < len(block):
                    data_buffer.write(QRCodeBuilder.binary_string(block[i], 8))

        #Add the error code blocks.
        #Write the buffer such that: block 1 byte 1, block 2 byte 2, etc.
        for i in range(error_info[0]):
            for block in error_blocks:
                data_buffer.write(QRCodeBuilder.binary_string(block[i], 8))

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
            bits = QRCodeBuilder.binary_string(0,4)
        else:
            #Make up any shortfall need with less than 4 zeros
            bits = QRCodeBuilder.binary_string(0, data_capacity - len(payload))

        return bits

    def delimit_words(self):
        """This method takes the existing encoded binary string
        and returns a binary string that will pad it such that
        the encoded string contains only full bytes.
        """
        bits_short = 8 - (len(self.buffer.getvalue()) % 8)
        
        #The string already falls on an byte boundary do nothing
        if bits_short == 0 or bits_short == 8:
            return None
        else:
            return QRCodeBuilder.binary_string(0, bits_short)

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
        matrix_size = _get_symbol_size(self.version, scale=1, quiet_zone=0)[0]

        #Create a template matrix we will build the codes with
        row = [' ' for x in range(matrix_size)]
        template = [deepcopy(row) for x in range(matrix_size)]

        #Add mandatory information to the template
        QRCodeBuilder.add_detection_pattern(template)
        self.add_position_pattern(template)
        self.add_version_pattern(template)

        #Create the various types of masks of the template
        self.masks = self.make_masks(template)

        self.best_mask = self.choose_best_mask()
        self.code = self.masks[self.best_mask]

    @staticmethod
    def add_detection_pattern(m):
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
            QRCodeBuilder.add_type_pattern(cur_mask, tables.type_bits[self.error][n])

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
        #    _png(m, self.version, 'mask-{0}.png'.format(i), 5)

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
        #        print('{0: >6}'.format(s), end='')
        #    print('{0: >7}'.format(totals[i]))
        #print('Mask Chosen: {0}'.format(totals.index(min(totals))))

        #The lowest total wins
        return totals.index(min(totals))

    @staticmethod
    def add_type_pattern(m, type_bits):
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


def _get_symbol_size(version, scale, quiet_zone=4):
    """See: QRCode.symbol_size()

    This function was abstracted away from QRCode to allow for the output of
    QR codes during the build process, i.e. for debugging. It works
    just the same except you must specify the code's version. This is needed
    to calculate the symbol's size.
    """
    #Formula: scale times number of modules plus the border on each side
    dim = version * 4 + 17
    dim += 2 * quiet_zone
    dim *= scale
    return dim, dim