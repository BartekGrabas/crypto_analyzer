from crypto_analyzer.main import create_data_directory


def test_create_data_directory(tmp_path):
    custom_dir = tmp_path / "data"
    create_data_directory(custom_dir)
    assert custom_dir.exists()
    assert custom_dir.is_dir()
