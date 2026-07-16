from samileides.config import ExperimentConfig
from samileides.data import repo_root


def test_load_smoke_config():
    cfg = ExperimentConfig.load(repo_root() / "configs" / "experiments" / "smoke.yaml")
    assert cfg.name == "smoke"
    assert cfg.data.source == "greek"
    assert cfg.model.d_model == 256
    assert cfg.tokenizer.vocab_size == 4000
    assert cfg.training.per_device_batch_size == 64
    assert cfg.inference.beam == 5
    assert cfg.probe is None


def test_load_smoke_big_config():
    cfg = ExperimentConfig.load(repo_root() / "configs" / "experiments" / "smoke_big.yaml")
    assert cfg.name == "smoke_big"
    assert cfg.model.d_model == 1024
    assert cfg.model.encoder_attention_heads == 16
    assert cfg.model.encoder_ffn_dim == 4096
    assert cfg.tokenizer.vocab_size == 4000
    assert cfg.training.lr_scheduler == "cosine"
    assert cfg.training.max_steps == 400
    assert cfg.probe is not None
    assert cfg.probe.every_steps == 100


def test_load_ie_big_config():
    cfg = ExperimentConfig.load(repo_root() / "configs" / "experiments" / "ie_big.yaml")
    assert cfg.name == "ie_big"
    assert cfg.data.selection == "experiments/selection-ie.csv"
    assert cfg.data.holdouts == "configs/holdouts-ie.yaml"
    assert cfg.data.source == "greek"
    assert cfg.model.d_model == 1024
    assert cfg.model.encoder_layers == 6
    assert cfg.model.decoder_layers == 6
    assert cfg.model.encoder_attention_heads == 16
    assert cfg.model.encoder_ffn_dim == 4096
    assert cfg.tokenizer.vocab_size == 32000
    assert cfg.training.lr == 5.0e-4
    assert cfg.training.lr_scheduler == "cosine"
    assert cfg.training.warmup_steps == 4000
    assert cfg.training.max_steps == 100000
    assert cfg.training.per_device_batch_size == 128
    assert cfg.training.gradient_accumulation == 2
    assert cfg.training.seed == 13
    assert cfg.probe is not None
    assert cfg.probe.every_steps == 1000
    assert cfg.probe.min_gain == 1.0
    assert cfg.probe.patience_steps == 20000


def test_load_ie_big_shareable_config():
    cfg = ExperimentConfig.load(
        repo_root() / "configs" / "experiments" / "ie_big_shareable.yaml"
    )
    assert cfg.name == "ie_big_shareable"
    assert cfg.data.selection == "experiments/selection-ie-shareable.csv"
    assert cfg.data.holdouts == "configs/holdouts-ie-shareable.yaml"
    assert cfg.model.d_model == 1024
    assert cfg.training.lr_scheduler == "cosine"
    assert cfg.training.per_device_batch_size == 128
    assert cfg.probe is not None


def test_unknown_yaml_keys_ignored(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(
        "name: x\nphase: one-to-many\n"
        "data:\n  selection: a.csv\n  holdouts: b.yaml\n  future_key: 1\n"
        "model:\n  d_model: 128\n",
        encoding="utf-8",
    )
    cfg = ExperimentConfig.load(p)
    assert cfg.data.selection == "a.csv"
    assert cfg.model.d_model == 128
