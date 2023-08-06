# IRescue

IRescue is a software for quantifying the expression of transposable elements (TEs) subfamilies in single cell RNA sequencing (scRNA-seq) data.
The core feature of IRescue is to consider all multiple alignments (i.e. non-primary alignments) of reads/UMIs mapping on multiple TEs in a BAM file, to better infer the TE subfamily of origin. IRescue implements a UMI error-correction, deduplication and quantification strategy that includes such alignments events. IRescue's output is compatible with most scRNA-seq analysis toolits, such as Seurat or Scanpy.

## Installation

We advise installing IRescue in a conda environment with all required software:

```bash
# clone this repository
git clone https://github.com/bepoli/irescue
cd irescue

# create a conda environment
conda create -f docker/environment.yaml -n irescue

# install irescue
conda activate irescue
pip install .

# test the installation
irescue --help
```

## Usage

Run `irescue --help` for an overview of the parameters.

IRescue generates TE counts in a sparse matrix format:

```
irescue_output/
├── barcodes.tsv.gz
├── features.tsv.gz
└── matrix.mtx.gz
```

### Use with Seurat

To integrate TE counts into an existing Seurat object containing gene expression data, they can be added as an additional assay:

```R
# import TE counts from IRescue output directory
irescue.data <- Seurat::Read10X('irescue_output/', gene.column = 1, cell.column = 1)

# create Seurat assay from TE counts
irescue.assay <- Seurat::CreateAssayObject(te.data)

# subset the assay by the cells already present in the Seurat object (in case it has been filtered)
irescue.assay <- subset(irescue.assay, colnames(irescue.assay)[which(colnames(irescue.assay) %in% colnames(seurat_object))])

# add the assay in the Seurat object
seurat_object[['TE']] <- irescue.assay
```

The result will be something like this:
```
An object of class Seurat 
32276 features across 42513 samples within 2 assays 
Active assay: RNA (31078 features, 0 variable features)
 1 other assay present: TE
```
