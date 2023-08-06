# -*- coding: utf-8 -*-
import os
import tensorflow as tf
import shutil
import tf2pb

#if not fastertransformer , don't advice change

try:
    #cuda 11.3 pip install fastertransformer==4.0.0.113
    #cuda 11.6 pip install fastertransformer==4.0.0.116
    import fastertransformer
    convert_config = {
        "fastertransformer": {
            "floatx": "float32",
            "remove_padding": False,
            "int8_mode": 0,  # need nvidia card supoort,do not suggest
        }
    }
except:
    convert_config = {}


# BertModel_module = load_model_tensor 加载 官方bert模型和fastertransformer模型
#如果是正常pb, 可以直接使用官方modeling 模块 import modeling

def load_model_tensor(bert_config_file,max_seq_len,num_labels):
    BertModel_module = tf2pb.get_modeling(convert_config)
    if BertModel_module is None:
        raise Exception('tf2pb get_modeling failed')
    bert_config = BertModel_module.BertConfig.from_json_file(bert_config_file)

    def create_model(bert_config, is_training, input_ids, input_mask, segment_ids, num_labels, use_one_hot_embeddings):
        """Creates a classification model."""
        model = BertModel_module.BertModel(
            config=bert_config,
            is_training=is_training,
            input_ids=input_ids,
            input_mask=input_mask,
            token_type_ids=segment_ids,
            use_one_hot_embeddings=use_one_hot_embeddings)

        output_layer = model.get_pooled_output()
        hidden_size = output_layer.shape[-1].value
        output_weights = tf.get_variable(
            "output_weights", [num_labels, hidden_size],
            dtype="float32",
            initializer=tf.truncated_normal_initializer(stddev=0.02))
        output_bias = tf.get_variable(
            "output_bias", [num_labels],
            dtype="float32",
            initializer=tf.zeros_initializer())
        logits = tf.matmul(output_layer, output_weights, transpose_b=True)
        logits = tf.nn.bias_add(logits, output_bias)
        probabilities = tf.nn.softmax(logits, axis=-1)
        return probabilities

    input_ids = tf.placeholder(tf.int32, (None, max_seq_len), 'input_ids')
    input_mask = tf.placeholder(tf.int32, (None, max_seq_len), 'input_mask')
    segment_ids = None
    # 这里简单使用分类，具体根据自己需求修改
    probabilities = create_model(bert_config, False, input_ids, input_mask, segment_ids, num_labels, False)
    save_config = {
        "input_tensor": {
            'input_ids': input_ids,
            'input_mask': input_mask
        },
        "output_tensor": {
            "pred_ids": probabilities
        },
    }
    return save_config

if __name__ == '__main__':

    # 训练ckpt权重
    weight_file = r'/home/tk/tk_nlp/script/ner/ner_output/bert/model.ckpt-2704'
    output_dir = r'/home/tk/tk_nlp/script/ner/ner_output/bert'

    bert_config_file = r'/data/nlp/pre_models/tf/bert/chinese_L-12_H-768_A-12/bert_config.json'
    if not os.path.exists(bert_config_file):
        raise Exception("bert_config does not exist")

    max_seq_len = 340
    num_labels = 16 * 4 + 1

    #normal pb
    pb_config = {
        "ckpt_filename": weight_file,  # 训练ckpt权重
        "save_pb_file": os.path.join(output_dir,'bert_inf.pb'),
    }
    #serving pb
    pb_serving_config = {
        'use':False,#默认注释掉保存serving模型
        "ckpt_filename": weight_file,  # 训练ckpt权重
        "save_pb_path_serving": os.path.join(output_dir,'serving'),  # tf_serving 保存模型路径
        'serve_option': {
            'method_name': 'tensorflow/serving/predict',
            'tags': ['serve'],
        }
    }

    if pb_config['save_pb_file'] and os.path.exists(pb_config['save_pb_file']):
        os.remove(pb_config['save_pb_file'])

    if pb_serving_config['use'] and pb_serving_config['save_pb_path_serving'] and os.path.exists(pb_serving_config['save_pb_path_serving']):
        shutil.rmtree(pb_serving_config['save_pb_path_serving'])


    def convert2pb(is_save_serving):
        def create_network_fn():
            save_config = load_model_tensor(bert_config_file=bert_config_file,max_seq_len=max_seq_len,num_labels=num_labels)
            save_config.update(pb_serving_config if is_save_serving else pb_config)
            return save_config

        if not is_save_serving:
            ret = tf2pb.freeze_pb(create_network_fn)
            if ret ==0:
                tf2pb.pb_show(pb_config['save_pb_file'])
            else:
                print('tf2pb.freeze_pb failed ',ret)
        else:
            ret = tf2pb.freeze_pb_serving(create_network_fn)
            if ret ==0:
                tf2pb.pb_serving_show(pb_serving_config['save_pb_path_serving'],pb_serving_config['serve_option']['tags'])  # 查看
            else:
                print('tf2pb.freeze_pb_serving failed ',ret)

    convert2pb(is_save_serving = False)
    if pb_serving_config['use']:
        convert2pb(is_save_serving = True)
