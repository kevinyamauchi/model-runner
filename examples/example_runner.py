import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str)
parser.add_argument("--job_prefix", type=str)
parser.add_argument("--output_base_dir", type=str)
parser.add_argument("--job_index", type=int)
parser.add_argument("--batch_size", type=float)
parser.add_argument("--lr", type=float)
parser.add_argument("--augment", type=bool)
args = parser.parse_args()

job_ind = args.job_index
job_prefix = args.job_prefix
print(f'{job_prefix}: job {job_ind}')

# add a pause to simulate work
time.sleep(300)
