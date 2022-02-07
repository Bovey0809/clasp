from datetime import datetime
import os
from pathlib import Path
import subprocess
import copy

# Note: Run preprocess_data.py file in the main repository directory or the preproc directory of the repository.


urls_download = ["https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.dat.gz",
        "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_trembl.dat.gz"]

print(f"{datetime.now()} - Start downloading files.")
path_current_dir = os.path.abspath(os.path.dirname(__file__))
path_data_dir = f'{path_current_dir.split("/preproc")[0]}/data'
paths_raw_data = []
for url in urls_download:
    print(f"{datetime.now()} - Start downloading from: {url}")
    Path(path_data_dir).mkdir(exist_ok=True)
    subprocess.run(["wget", url, "-P", path_data_dir])
    paths_raw_data.append(f'{path_data_dir}/{url.split("/")[-1]}')
    print(f"{datetime.now()} - Download finished.")


print(f"{datetime.now()} - Decompress downloaded files.")
paths_data = []
for path_raw in paths_raw_data:
    path_decomp = path_raw.split(".gz")[0]
    print(f"{datetime.now()} - Decompress: {path_raw}")
    subprocess.run(["gunzip", path_raw, path_decomp])
    paths_data.append(path_decomp)
    print(f"{datetime.now()} - Decompressed to: {path_decomp}")


print(f"{datetime.now()} - Preprocessing files and saving to csv.")
# Raw data setup see user manual: https://web.expasy.org/docs/userman.html
linetype_conversion = {
    "ID": "id",
    "AC": "accn",
    "DT": "date",
    "DE": "desc",
    "GN": "gene",
    "OS": "spec",
    "OG": "orga",
    "OC": "clas",
    "OX": "taxo",
    "OH": "host",
    "RN": "refn",
    "RP": "refp",
    "RC": "refc",
    "RX": "refx",
    "RG": "refg",
    "RA": "refa",
    "RT": "reft",
    "RL": "refl",
    "CC": "text",
    "DR": "xdb",
    "PE": "exist",
    "KW": "kw",
    "FT": "ft",
    "SQ": "seqh",
    "  ": "seq",
}


preprocessing_fields = ["id","accn","date","desc","gene","spec","orga","clas","taxo","host","refn", "refp", "refc", "refx", "refg", "refa", "reft", "refl", "text","xdb","ft","exist","kw","seqh","seq"]

def get_csv(path, fields):
    path_out = f'{path.split(".")[0]}.csv'
    print(f"{datetime.now()} - Processing: {path}")
    print(f"{datetime.now()} - Saving to:  {path_out}")
    print("Processing file line:")

    i = 0
    data = {k: "" for k in fields}
    with open(path, 'r') as rf, open(path_out, 'w') as wf:
        while True:
            if i == 0: # write header to csv
                header = ",".join(fields)+"\n"
                wf.write(header)

            if i % 1_000_000 == 0:
                print(i, end=", ")
            i += 1

            rline = rf.readline()

            if rline.startswith("CC   ----") or \
               rline.startswith("CC   Copy") or \
               rline.startswith("CC   Dist"):
                continue
            elif rline == "": # EOF is empty string
                print(f"\n{datetime.now()} - Processing complete.")
                break

            elif rline.startswith("//"): # end of entry, save line to csv file
                for key in data:    
                    if key == "seq":
                        data[key] = data[key].replace(" ","") # remove spaces in AA sequence

                wline = ",".join([x.replace(",",";") for x in data.values()])+"\n"
                wf.write(wline)
                data = {k: "" for k in fields} # create new empty data dict
                continue

            key = linetype_conversion[rline[:2]] # get line key
            content = " ".join(rline[5:].split()) # get line content
            data[key] += content if data[key] == "" else f' {content}'
    return path_out

paths_csv = []
for path in paths_data:
    path_out = get_csv(path, fields=preprocessing_fields)
    paths_csv.append(path_out)
    print(f"{datetime.now()} - Preprocessed file saved to: {path_out}")


#print(f"{datetime.now()} - Getting string lengths for every column.")
#cols = copy.deepcopy(preprocessing_fields)
#cols.append("text_all")
#
#def get_cols_len_csv(path, cols):
#    path_out = path.split(".")[0]+"_len.csv"
#    print(f"Processing: {path}")
#    print(f"Saving to:  {path_out}")
#    i = 0
#    with open(path, 'r') as rf, open(path_out, 'w') as wf:
#        while True:
#            if i % 1_000_000 == 0:
#                print(i, end=", ")
#            i += 1
#
#            line = rf.readline()
#            if line == "": # EOF is an empty string
#                break
#
#            line = line.replace("\n","").split(",")
#
#            if i == 1: # get index values for the wanted columns
#                idx = dict()
#                for c in cols:
#                    if c == "text_all":
#                        continue
#                    idx[c] = line.index(c)
#
#                wline = ",".join(cols)+"\n" # write header
#                wf.write(wline)
#                continue
#
#            out = []
#            text_all = 0
#            for c in cols:
#                if c == "id":
#                    out.append(line[idx[c]].split(" ")[0])
#                elif c == "text_all":
#                    out.append(str(text_all))
#                else:
#                    length = len(line[idx[c]])
#                    text_all += length
#                    out.append(str(length))
#
#            wline = ",".join(out)+"\n"
#            wf.write(wline)
#    return path_out
#
#for path in paths_csv:
#    path_out = get_cols_len_csv(path, cols)
#    print(f"{datetime.now()} - String lengths data saved to: {path_out}")


print(f"{datetime.now()} - Merging preprocessed csv files into one csv file.")
path_csv_full = f'{path_data_dir}/uniprot_full.csv'
subprocess.run(["cat", paths_csv[0], f"<(tail +2 {paths_csv[1]})", ">", path_csv_full])
print(f"{datetime.now()} - Merged files saved to: {path_csv_full}")


print(f"{datetime.now()} - Data preprocessing done.")

