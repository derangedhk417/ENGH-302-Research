import csv
from math import pi as pi

idx_part_number = 2
idx_capacitance = 14
idx_voltage     = 16
idx_size        = 23
idx_height      = 24

# Strips off whitespace and then retrieves the first chunk of numeric
# characters as a string.
def separate_numeric_front(s):
    if s.strip() == '-':
        raise Exception()

    chars = '0123456789.'
    t = s.strip()
    result = ''
    for i in t:
        if i in chars:
            result = result + i
        else:
            break
    return result

# Strips off whitespace and then retrieves all of the text after
# the first chunk of numeric characters.
def separate_text_end(s):
    if s.strip() == '-':
        raise Exception()

    chars = '0123456789.'
    t = s.strip()

    result = ''

    idx = 0
    while idx < len(t):
        if t[idx] not in chars:
            break
        idx += 1

    while idx < len(t):
        result = result + t[idx]
        idx += 1

    return result

def mean(data, key):
    s = 0.0
    for i in data:
        s += key(i)

    return s / len(data)


def median(data, key):
    # Sorted data expected
    return key(data[int(len(data) / 2)])

# Handles the millimeter scale dimensions present
# in the spreadsheet.
def read_dimensions_from_parentheses(s):
    if s.strip() == '-':
        raise Exception()

    chars = '0123456789.'
    dims = ['']

    idx              = 0
    in_parentheses   = False
    while idx < len(s):
        if in_parentheses:
            if s[idx] == ')':
                break
            else:
                if s[idx] == 'x':
                    dims.append('')
                elif s[idx] in chars:
                    dims[-1] = dims[-1] + s[idx]
        else:
            if s[idx] == '(':
                in_parentheses = True
        
        idx += 1

    return dims



# Holds the relevent defining information on a supercapacitor for
# the purposes of this analysis.
class Supercapacitor:
    def __init__(self, row):
        self.capacitance    = 0.0 # Farads
        self.voltage        = 0.0 # Volts
        self.volume         = 0.0 # Cubic Meters
        self.energy         = 0.0 # Joules
        self.energy_density = 0.0 # Joules per Cubic Meter
        self.part_number    = row[idx_part_number]

        self.capacitance    = self.get_capacitance(row)
        self.voltage        = self.get_voltage(row)
        self.volume         = self.get_volume(row)
        self.energy         = 0.5*self.capacitance*(self.voltage**2)
        self.energy_density = self.energy / self.volume

    def get_capacitance(self, row):
        raw_cap    = row[idx_capacitance]
        cap_number = float(separate_numeric_front(raw_cap))
        unit       = separate_text_end(raw_cap)

        if unit[0] == 'm':
            # Millifarads
            return cap_number / 1000.0
        elif unit[0] == 'F':
            # Farads
            return cap_number
        else:
            print(unit)
            raise Exception()

    def get_voltage(self, row):
        return float(separate_numeric_front(row[idx_voltage]))

    def get_volume(self, row):
        dims1 = read_dimensions_from_parentheses(row[idx_size])
        dim2  = read_dimensions_from_parentheses(row[idx_height])

        if len(dims1) == 1:
            # Dimensions are in diameter and height
            return ((float(dims1[0]) / 2000.0)**2) * pi * (float(dim2[0]) / 1000.0)
        elif len(dims1) == 2:

            # Dimensions are in length, width and height.
            return (float(dims1[0]) / 1000.0) * (float(dims1[1]) / 1000.0) * (float(dim2[0]) / 1000.0)
        else:
            print(row[idx_size])
            print(row[idx_height])
            raise Exception()

    def __str__(self):
        out = ''
        out += 'part number:    %s\n'%self.part_number
        out += 'capacitance:    %f\n'%self.capacitance
        out += 'voltage:        %f\n'%self.voltage
        out += 'volume:         %f\n'%self.volume
        out += 'energy:         %f\n'%self.energy
        out += 'energy density: %f\n'%self.energy_density
        return out


if __name__ == '__main__':
    files = [
        'download (1).csv',
        'download (2).csv',
        'download (3).csv'
    ]

    raw_data = []

    for file in files:
        with open(file) as csvfile:
            r = csv.reader(csvfile)
            temp = []
            for row in r:
                temp.append(row)
            raw_data.extend(temp[1:])

    unparseable = 0
    data        = []
    for i in raw_data:
        try:
            cap = Supercapacitor(i)
            data.append(cap)
        except:
            unparseable += 1


    print('Processed %d capacitors'%(len(data) + unparseable))
    print('%d were unparseable'%(unparseable))
    
    print('')
    print('Capacitance: ')
    select_capacitance = lambda x: x.capacitance

    caps_sort = sorted(data, key=select_capacitance)
    print('\tMinimum: %4.4f F'%(caps_sort[0].capacitance))
    print('\tMaximum: %4.4f F'%(caps_sort[-1].capacitance))
    print('\tMean:    %4.4f F'%(mean(caps_sort, key=select_capacitance)))
    print('\tMedian:  %4.4f F'%(median(caps_sort, key=select_capacitance)))

    print('')
    print('Voltage: ')
    select_voltage = lambda x: x.voltage

    volt_sort = sorted(data, key=select_voltage)
    print('\tMinimum: %3.1f V'%(volt_sort[0].voltage))
    print('\tMaximum: %3.1f V'%(volt_sort[-1].voltage))
    print('\tMean:    %3.1f V'%(mean(volt_sort, key=select_voltage)))
    print('\tMedian:  %3.1f V'%(median(volt_sort, key=select_voltage)))


    print('')
    print('Volume: ')
    select_volume = lambda x: x.volume

    vol_sort = sorted(data, key=select_volume)
    print('\tMinimum: %4.15f m³'%(vol_sort[0].volume))
    print('\tMaximum: %4.2f m³'%(vol_sort[-1].volume))
    print('\tMean:    %4.10f m³'%(mean(vol_sort, key=select_volume)))
    print('\tMedian:  %4.10f m³'%(median(vol_sort, key=select_volume)))

    print('')
    print('Energy: ')
    select_energy = lambda x: x.energy

    energy_sort = sorted(data, key=select_energy)
    print('\tMinimum: %4.4f J'%(energy_sort[0].energy))
    print('\tMaximum: %4.4f J'%(energy_sort[-1].energy))
    print('\tMean:    %4.4f J'%(mean(energy_sort, key=select_energy)))
    print('\tMedian:  %4.4f J'%(median(energy_sort, key=select_energy)))

    print('')
    print('Energy Density: ')
    select_ed = lambda x: x.energy_density

    ed_sort = sorted(data, key=select_ed)
    print('\tMinimum: %.4f J / m³'%(ed_sort[0].energy_density))
    print('\tMaximum: %.4f J / m³'%(ed_sort[-1].energy_density))
    print('\tMean:    %.4f J / m³'%(mean(ed_sort, key=select_ed)))
    print('\tMedian:  %.4f J / m³'%(median(ed_sort, key=select_ed)))