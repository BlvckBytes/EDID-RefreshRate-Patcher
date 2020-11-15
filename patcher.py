import re
import sys

def patch_edid(value):
    # Set refresh rate to 48Hz
    # EDID structure: https://en.wikipedia.org/wiki/Extended_Display_Identification_Data
    edid = value[:108] + 'a6a6' + value[112:] 
    
    # Recalculate checksum after change
    data = [int(edid[i:i + 2], 16) for i in range(0, len(edid), 2)]
    checksum = hex(256 - sum(data[:-1]) % 256)[2:]
    
    # Return value with new checksum
    return edid[:-2] + checksum

# Open input file
with open('display_info.txt', 'r') as inp_file:
    
    # Constants needed for processing
    begin_marker = 'EDID:' # xrandr starts of EDIDs like this
    edid_bytelen = 128 # There are 128 bytes within an EDID
    edid_hexlen = edid_bytelen * 2
    
    # Read all file lines
    # Strip \t, \n and spaces, since they're not needed for parsing
    lines = list(map(lambda x: re.sub(r'[\t\n ]', '', x), inp_file.readlines()))
    
    # Now concat the whole content into one single string
    info = ''.join(lines)
    
    # Create a list of EDID occurrences 
    occurrences = []
    
    # Search all occurrence-indices of EDID beginnings
    occ_index = info.find(begin_marker)
    while occ_index != -1:
        # Substring without the begin-marker
        substr_index = occ_index + len(begin_marker)
        occurrences.append(info[substr_index:substr_index + edid_hexlen].upper())
        
        # Try to find another occurrence
        occ_index = info.find(begin_marker, occ_index + 1)
    
    # No EDIDs available
    if len(occurrences) == 0:
        print('Could not find any EDIDs, please check your input!')
        sys.exit()
    
    # Multiple EDIDs found, prompt for desired one
    desired_index = 0
    if len(occurrences) > 1:
        print('There are multiple EDIDs available, please choose one:')
        
        c = 0
        for edid in occurrences:
            print(f'[{c}]: {edid[0:30]}...{edid[edid_hexlen - 30:edid_hexlen]}')
            c += 1
        
        desired_index = int(input('Your selection: '))
        print()
    
    # This will now be the target EDID
    target_edid = occurrences[desired_index]
    
    # Patch the target value
    patched_edid = patch_edid(target_edid)
    
    # Print patch-instructions
    print('Patched your EDID!')
    print('Please add it to DeviceProperties/Add/PciRoot(0x0)/Pci(0x2,0x0) like this:')
    print('Create a new entry: AAPL00,override-no-connect (with type data)')
    print('And set the value to:\n')
    print(patched_edid.upper())
