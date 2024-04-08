import pandas

def serialize(entry):
    keys = entry.keys().drop(["Label"])
    prompt = ','.join([f"{key}:{entry[key]}" for key in keys])
    label = entry["Label"]
    return f"<s>[INST] {prompt} [/INST] {label} </s>"

def get_pcap_dataframe(path):
    df = pandas.read_csv(path, dtype=str)
    df = df.rename(columns=lambda x: x[1:].replace(' ', '_'))
    #df['Label'] = df['Label'].apply(lambda x: 0 if x=='BENIGN' else 1)


    #cols = cols.drop(columns=['Label'])
    df["text"] = df.apply(serialize, axis=1)
    
    return df.loc[:, ['text']]

#DATA_FILE = '/scratch/bae9wk/datasets/PCAP/CSV-01-12/01-12/Syn.csv'
#get_pcap_dataframe(DATA_FILE).to_csv('/scratch/bae9wk/datasets/PCAP/CSV-01-12/01-12/reformatted_Syn.csv')