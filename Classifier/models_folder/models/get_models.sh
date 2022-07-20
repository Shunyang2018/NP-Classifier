rm CLASS SUPERCLASS PATHWAY -r
rm *hdf5

unzip models.zip
mkdir -p CLASS/000001
mkdir -p SUPERCLASS/000001
mkdir -p PATHWAY/000001

python ./convert_keras_to_tf.py NP_classifier_class_V1.hdf5 CLASS/000001
python ./convert_keras_to_tf.py NP_classifier_superclass_V1.hdf5 SUPERCLASS/000001
python ./convert_keras_to_tf.py NP_classifier_pathway_V1.hdf5 PATHWAY/000001
