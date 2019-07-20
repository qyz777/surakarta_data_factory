from nemesis.min_max_search import MinMaxSearch
from nemesis.depth_search import DepthSearch
from nemesis.search import Search, SearchConfig, SearchType


def build(game_info: dict, ai_camp: int, config: SearchConfig) -> Search:
    if config.search_type == SearchType.MIN_MAX:
        return MinMaxSearch(game_info, ai_camp, config)
    else:
        return DepthSearch(game_info, ai_camp, config)
