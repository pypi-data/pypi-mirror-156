import json

import numpy as np
import xgboost


def mvt_to_xgboost_dict(trees, feature_names):
    feature_names = list(feature_names)
    base_score = 0
    num_trees = len(trees)
    
    xgb_trees = []
    missing = 0
    for i, tree in enumerate(trees):
        if len(tree) == 1 and tree[0][-1] == -1:
            num_trees -= 1
            missing += 1
            base_score += np.log(tree[0][1])
            continue
            
        i = i - missing
            
        left_children = [
            -1 if f == -1 else j + 1
            for j, (*_, f) in enumerate(tree)
        ]
        right_children = [
            -1 if f == -1 else int(j + ind + 1)
            for j, (ind, *_, f) in enumerate(tree)
        ]
        parents = {
            v: k
            for d in [left_children, right_children]
            for k, v in enumerate(d)
            if v != -1
        }
        parents = [
            parents.get(v, 2**31 - 1)
            for v in range(len(tree))
        ]
        
        xgb_trees.append({
            "categories": [],
            "categories_nodes": [],
            "categories_segments": [],
            "categories_sizes": [],
            "id": i,
            "tree_param": {
                "num_deleted": "0",
                "num_feature": str(len(feature_names)),
                "num_nodes": str(len(tree)),
                "size_leaf_vector": "0"
            },
            "split_type": [0] * len(tree),
            "split_indices": [max(0, ind) for *_, ind in tree],
            "default_left": [0 if d == "right" else 1 for *_, d, _ in tree],
            "split_conditions": [t if f >= 0 else np.log(t) for _, t, _, f in tree],
            "loss_changes": [0.1] * len(tree),
            "parents": parents,
            "left_children": left_children,
            "right_children": right_children,
            "sum_hessian": [0.] * len(tree),
            "base_weights": [0.1] * len(tree),
        })
        
    xgb_trees[0]['split_conditions'] = [
        t + base_score if left_child == right_child == -1 else t
        for left_child, right_child, t in zip(
            xgb_trees[0]['left_children'], 
            xgb_trees[0]['right_children'], 
            xgb_trees[0]['split_conditions']
        )
    ]
        
    return {
        "learner": {
            "attributes": {
                "best_iteration": str(num_trees - 1),
                "best_ntree_limit": str(num_trees)
            },
            "feature_names": feature_names,
            "feature_types": ["float"] * len(feature_names),
            "gradient_booster": {
                "model": {
                    "gbtree_model_param": {
                        "num_parallel_tree": "1",
                        "num_trees": str(num_trees),
                        "size_leaf_vector": "0"
                    },
                    "tree_info": [0] * num_trees,
                    "trees": xgb_trees
                },
                "name": "gbtree"
            },
            "learner_model_param": {
                # xgboost 1.6.1 ignores "base_score",
                # so we use 0 in case one day it doesn't
                "base_score": "0", 
                "num_class": "0",
                "num_feature": str(len(feature_names)),
                "num_target": "1"
            },
            "objective": {
                "name": "reg:squarederror",
                "reg_loss_param": {
                    "scale_pos_weight": "1"
                }
            }
        },
        "version": [1, 6, 1]
    }


def dict_to_xgboost(j):
    return xgboost.Booster(model_file=bytearray(json.dumps(j).encode()))


def mvt_to_xgboost(trees, feature_names):
    j = mvt_to_xgboost_dict(trees, feature_names)
    b = dict_to_xgboost(j)
    return b
