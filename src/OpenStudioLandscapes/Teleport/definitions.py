from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.Teleport.assets
import OpenStudioLandscapes.Teleport.constants

assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.Teleport.assets],
)

constants = load_assets_from_modules(
    modules=[OpenStudioLandscapes.Teleport.constants],
)


defs = Definitions(
    assets=[
        *assets,
        *constants,
    ],
)
