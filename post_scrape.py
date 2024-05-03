import os
path = "analysis/checkpoint-9750/"

benign = path + 'Benign/'
syn = path + 'Syn/'

fp, fn, tp, tn = 0 ,0, 0, 0

def is_syn(s):
    syn = ['this is a SYN attack',
           'it appears that this is a SYN attack',
           'it does appear to be a SYN attack']
    
    for substr in syn:
        if substr in s: return True
    return False
    
def is_benign(s):
    benign = ['it does not appear to be a SYN attack','it is not a SYN attack', 'this is not a SYN attack',
    ]

    for substr in benign:
        if substr in s: return True
    return False
    

for filename in os.listdir(benign):
    with open(benign + filename) as f:
        response = f.read()
        if is_syn(response):
            fp += 1
        elif is_benign(response):
            tn += 1
        else:
            print("Error on", benign+filename)
            exit()
for filename in os.listdir(syn):
    with open(syn + filename) as f:
        response = f.read()
        if is_syn(response):
            tp += 1
        elif is_benign(response):
            fn += 1
        else:
            print("Error on", syn+filename)
            exit()

print("False positives:", fp)
print("False negatives:", fn)
print("True positives:", tp)
print("True negatives:", tn)