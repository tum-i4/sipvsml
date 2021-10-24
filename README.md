# SIPvsML

## Software Integrity Protection Versus Machine Learning attacks
This repository hosts implementation code for [Master's Thesis](thesis_nika_dogonadze_sip_vs_ml.pdf). The work evaluates effectiveness of 
Obfuscation \& Software Integrity Protection schemes against Machine Learning-based attacks.

The image below summarizes the results:  
<a href="https://raw.githubusercontent.com/tum-i4/sipvsml/master/diagrams/SIPvsML_summary_results.png"><img src="https://raw.githubusercontent.com/tum-i4/sipvsml/master/diagrams/SIPvsML_summary_results.png" align="center" height="350"></a>


### Project Structure
- [/sip_ml_pipeline](https://github.com/tum-i4/sipvsml/tree/master/sip_ml_pipeline) - Contains entire ML pipeline from data generation to rendering result charts 
- [/notebooks](https://github.com/tum-i4/sipvsml/tree/master/notebooks) - Interactive notebooks for data examination
- [/code2vec](https://github.com/Megatvini/code2vec) - Reference to external code embedding component
- [/diagrams](https://github.com/tum-i4/sipvsml/tree/master/diagrams) - Draw.io diagram xml file sources


### Requirements
- [Python3](https://www.python.org/downloads/) 3.8.5
- [Go](https://golang.org/doc/install) 1.16
- [Docker](https://docs.docker.com/get-docker/) 20.10.7
- [Bash](https://help.ubuntu.com/community/Beginners/BashScripting) 5.1.8
- [LLVM](https://llvm.org/) 10.0.2
- Python Libraries - [requirements.txt](requirements.txt)

```shell
python3 -m venv venv &&
source venv/bin/activate &&
pip install -r requirements.txt
```

### Training Data
* [Full Data](https://ndogonadze-data-backups.s3.eu-west-1.amazonaws.com/sip_dataset.tar.gz?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQI6VN5LXY2V3B57W%2F20211024%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Date=20211024T162243Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=0dd3087ca7d973a6c44c5ad953aaac495030e06d2190e4267fea219115c767c2)
* [Raw Data](https://ndogonadze-data-backups.s3.eu-west-1.amazonaws.com/sip_dataset_raw_bc.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQI6VN5LXY2V3B57W%2F20211024%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Date=20211024T161858Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=92d9c411b200dc71e92dbb8c9d270676acfeb5c898240f58160b4c1c2f52e1d7)
* [Results Data](https://ndogonadze-data-backups.s3.eu-west-1.amazonaws.com/sip_dataset_raw_bc.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQI6VN5LXY2V3B57W%2F20211024%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Date=20211024T161858Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=92d9c411b200dc71e92dbb8c9d270676acfeb5c898240f58160b4c1c2f52e1d7)

The full training data, including features, splits and results is ~500GB. Raw Data only include source
programs without preprocessing or feature extraction. Results Data only contains result `.json` files and 
model weights.
