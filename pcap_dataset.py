import pandas
import argparse

i = 0
def serialize(entry):
    global i
    keys = entry.keys().drop(["Label"])
    prompt = ','.join([f"{key}:{entry[key]}" for key in keys])
    label = "Yes, it is a SYN attack" if entry["Label"].upper() =="SYN" else "No, it is a benign packet."
    print(label, i)
    i += 1
    return f"<s>[INST] Given the following information, is this packet a SYN attack?: [{prompt}] [/INST] {label} </s>"

def get_pcap_dataframe(path):
    df = pandas.read_csv(path, dtype=str)
    df = df.rename(columns=lambda x: x[1:].replace(' ', '_'))
    #df['Label'] = df['Label'].apply(lambda x: 0 if x=='BENIGN' else 1)


    #cols = cols.drop(columns=['Label'])
    df["text"] = df.apply(serialize, axis=1)
    
    return df.loc[:, ['text']]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--save_to", type=str, default="", help="Path where the LLaMA-friendly dataset should be saved"
    )
    parser.add_argument(
        "--read_from", type=str, default="", help="Path of raw CSV"
    )
    args = parser.parse_args()
    if args.read_from and args.save_to:
        get_pcap_dataframe(args.read_from).to_csv(args.save_to)
