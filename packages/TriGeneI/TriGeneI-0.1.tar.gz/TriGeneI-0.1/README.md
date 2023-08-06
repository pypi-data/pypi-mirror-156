# TGMI
Rewrite TGMI network inference using Python

## example
Download and enter into the TGMI directory
~~~shell
cd TGMI
python TGMI.py -i  example/expression.txt -t example/tfs.txt -g example/genes.txt -o tgmi.txt
~~~
input file format see [example](./example)  

There will be three outputs:
1. tgmi_network.txt  
2. tgmi_TF.txt
3. tgmi_Gene.txt

## Reference
Chathura Gunasekara, Kui Zhang, Wenping Deng, Laura Brown, Hairong Wei, TGMI: an efficient algorithm for identifying pathway regulators through evaluation of triple-gene mutual interaction, Nucleic Acids Research, Volume 46, Issue 11, 20 June 2018, Page e67, https://doi.org/10.1093/nar/gky210
 
