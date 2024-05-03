import pandas
import argparse
import os
from tqdm.auto import tqdm

def label_entry(entry):
    keys = entry.keys().drop(["Label"])
    prompt = ','.join([f"{key}:{entry[key]}" for key in keys])
    label = "Yes, it is a SYN attack" if entry["Label"].upper() == "SYN" else "No, it is a benign packet."
    text = f"<s>[INST] Given the following information, is there a SYN attack in any of the following packet flows?: [{prompt}] [/INST] {label} </s>"
    return text


def load_dataframe_from_dir(path: str, nrows=None):
    print(f'recursively loading dataframes from dir: {path}')
    csv_files = []
    for root, _, files in os.walk(path):
        for name in files:
            if name.endswith('.csv'):
                csv_files.append(os.path.join(root, name))

    csv_files = [file for file in csv_files if not 'venv' in file]

    if len(csv_files) == 0:
        raise ValueError(f'no CSV files in dir: {path}')
    
    dfs = []
    for csv in tqdm(csv_files):
        try:
            dfs.append(pandas.read_csv(csv, dtype=str, nrows=nrows))
        except pandas.errors.MergeError:
            print(f'MergeError on {csv}')

    return pandas.concat(dfs)

def get_pcap_dataframe(path, nrows=None):
    df = load_dataframe_from_dir(path, nrows)

    print(f'formatting dataframe')
    df = df.rename(columns=lambda x: x.replace(' ', '_') if not x.startswith(' ') else x[1:].replace(' ', '_'))

    df = df.drop(['Unnamed:_0', 'Flow_ID',
       'Flow_IAT_Mean', 'Flow_IAT_Std', 'Flow_IAT_Max', 'Flow_IAT_Min',
       'Fwd_IAT_Total', 'Fwd_IAT_Mean', 'Fwd_IAT_Std', 'Fwd_IAT_Max',
       'Fwd_IAT_Min', 'Fwd_IAT_Total', 'Bwd_IAT_Mean', 'Bwd_IAT_Std',
       'Bwd_IAT_Max', 'Bwd_IAT_Min', 'Fwd_PSH_Flags', 'Bwd_PSH_Flags',
       'Fwd_URG_Flags', 'Bwd_URG_Flags', 'Fwd_Header_Length',
       'Bwd_Header_Length', 'Fwd_Packets/s', 'Bwd_Packets/s',
       'Min_Packet_Length', 'Max_Packet_Length', 'Packet_Length_Mean',
       'Packet_Length_Std', 'Packet_Length_Variance', 'Down/Up_Ratio',
       'Average_Packet_Size', 'Avg_Fwd_Segment_Size', 'Avg_Bwd_Segment_Size',
       'Fwd_Header_Length.1', 'Fwd_Avg_Bytes/Bulk', 'Fwd_Avg_Packets/Bulk',
       'Fwd_Avg_Bulk_Rate', 'Bwd_Avg_Bytes/Bulk', 'Bwd_Avg_Packets/Bulk',
       'Fwd_Avg_Bulk_Rate', 'Subflow_Fwd_Packets', 'Subflow_Fwd_Bytes',
       'Subflow_Bwd_Packets', 'Subflow_Bwd_Bytes', 'Init_Win_bytes_forward',
       'Init_Win_bytes_backward', 'act_data_pkt_fwd', 'min_seg_size_forward',
       'Active_Mean', 'Active_Std', 'Active_Max', 'Active_Min', 'Idle_Mean',
       'Idle_Std', 'Idle_Max', 'Idle_Min', 'SimillarHTTP', 'Inbound'], axis=1)

    df = df.dropna(subset='Label')
    mask = df['Label'] != 'Syn'

    df = pandas.concat([df[df['Label'] == 'Syn'], df[df['Label'] == 'BENIGN']])

    print('percent BENIGN:', len(df[df['Label'] == 'BENIGN']) / len(df[df['Label'] == 'Syn']))

    df["text"] = df.apply(label_entry, axis=1)
    df = df.dropna()

    return pandas.DataFrame(data=df, columns=['text'])

def serialize(entry):
    keys = entry.keys().drop(["Label"])
    prompt = ','.join([f"{key}:{entry[key]}" for key in keys])
    label = "Yes, it is a SYN attack" if entry["Label"].upper() =="SYN" else "No, it is a benign packet."
    return f"<s>[INST] Given the following information, is this packet a SYN attack?: [{prompt}] [/INST] {label} </s>"

def get_pcap_dataframe_legacy(path):
    '''
    Converts each line of the pcap dataset csv into a 10-packet window.
    '''
    df = pandas.read_csv(path, dtype=str)
    df = df.rename(columns=lambda x: x.replace(' ', '_') if not x.startswith(' ') else x[1:].replace(' ', '_'))
    df["text"] = df.apply(serialize, axis=1)

    df = df.drop(['Unnamed:_0', 'Flow_ID',
       'Flow_IAT_Mean', 'Flow_IAT_Std', 'Flow_IAT_Max', 'Flow_IAT_Min',
       'Fwd_IAT_Total', 'Fwd_IAT_Mean', 'Fwd_IAT_Std', 'Fwd_IAT_Max',
       'Fwd_IAT_Min', 'Fwd_IAT_Total', 'Bwd_IAT_Mean', 'Bwd_IAT_Std',
       'Bwd_IAT_Max', 'Bwd_IAT_Min', 'Fwd_PSH_Flags', 'Bwd_PSH_Flags',
       'Fwd_URG_Flags', 'Bwd_URG_Flags', 'Fwd_Header_Length',
       'Bwd_Header_Length', 'Fwd_Packets/s', 'Bwd_Packets/s',
       'Min_Packet_Length', 'Max_Packet_Length', 'Packet_Length_Mean',
       'Packet_Length_Std', 'Packet_Length_Variance', 'Down/Up_Ratio',
       'Average_Packet_Size', 'Avg_Fwd_Segment_Size', 'Avg_Bwd_Segment_Size',
       'Fwd_Header_Length.1', 'Fwd_Avg_Bytes/Bulk', 'Fwd_Avg_Packets/Bulk',
       'Fwd_Avg_Bulk_Rate', 'Bwd_Avg_Bytes/Bulk', 'Bwd_Avg_Packets/Bulk',
       'Fwd_Avg_Bulk_Rate', 'Subflow_Fwd_Packets', 'Subflow_Fwd_Bytes',
       'Subflow_Bwd_Packets', 'Subflow_Bwd_Bytes', 'Init_Win_bytes_forward',
       'Init_Win_bytes_backward', 'act_data_pkt_fwd', 'min_seg_size_forward',
       'Active_Mean', 'Active_Std', 'Active_Max', 'Active_Min', 'Idle_Mean',
       'Idle_Std', 'Idle_Max', 'Idle_Min', 'SimillarHTTP', 'Inbound'], axis=1)
    
    return pandas.DataFrame(data=df, columns=['text'])
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--save_to", type=str, default="", help="Path where the LLaMA-friendly dataset should be saved"
    )
    parser.add_argument(
        "--read_from", type=str, default="", help="path to a directory to be recursively searched for CSV files"
    )
    parser.add_argument(
        "--nrows", type=int, default=None, help="number of rows to read from each csv file"
    )
    args = parser.parse_args()
    if args.read_from and args.save_to:
        get_pcap_dataframe(args.read_from, args.nrows).to_csv(args.save_to)
