from torchrec.modules.embedding_configs import (
    DataType,
    EmbeddingBagConfig,
    EmbeddingConfig,
)
from torchrec.modules.embedding_modules import (
    EmbeddingBagCollection,
)
import torchrec
import torch
from torchrec.models.dlrm import DLRM, DLRMTrain
from torchrec.distributed.fused_embeddingbag import FusedEmbeddingBagCollectionSharder
from torchrec.modules.fused_embedding_modules import fuse_embedding_optimizer

eb1_config = EmbeddingBagConfig(
            name="t1",
            embedding_dim=16,
            num_embeddings=1000000000,
            feature_names=["f1"],
)
embedding_bag_collection = EmbeddingBagCollection(
        tables=[eb1_config],
        device=torch.device("meta"),
)
device=torch.device("cuda")
dlrm_model = DLRM(
        embedding_bag_collection,
        dense_in_features=1024,
        dense_arch_layer_sizes=[512, 256, 16],
        over_arch_layer_sizes=[512, 512, 256, 1],
        dense_device=device,
    )
  
model = DLRMTrain(dlrm_model)
model = fuse_embedding_optimizer(
        model,
        optimizer_type=torchrec.optim.RowWiseAdagrad,
        optimizer_kwargs={
            "lr": 0.02,
            "eps": 0.002,
        },
        device=torch.device("meta"),
    ) 

from torchrec.distributed.planner import (
    EmbeddingShardingPlanner,
    Topology,
)
planner = EmbeddingShardingPlanner(
                topology=Topology(
                    local_world_size=8,
                    world_size=8,
                    compute_device="cuda",
                )
            )
plan = planner.plan(model, [FusedEmbeddingBagCollectionSharder()])
print(plan)