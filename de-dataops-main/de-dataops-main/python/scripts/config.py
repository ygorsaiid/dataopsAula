" Arquivo de Configuração"

import os
local_path = os.path.abspath(os.getcwd())
data_path = os.path.dirname(local_path)

configs = {
    "meta_path": f"{local_path}/scripts/metadado.xlsx",
    "raw_path": f"{local_path}/data/raw/raw_",
    }
