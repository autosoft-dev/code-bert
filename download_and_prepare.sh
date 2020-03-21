wget https://s3.amazonaws.com/code-search-net/CodeSearchNet/v2/python.zip
unzip python.zip

mkdir .data
cp -r python .data/

rm -rf python
mv python.zip python_dedupe_definitions_v2.pkl python_licenses.pkl ../