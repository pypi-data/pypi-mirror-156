from cardtrader.service import CardTrader


def test_games(session: CardTrader):
    results = session.games()
    result = [x for x in results if x.game_id == 1]
    assert len(result) == 1
    assert result[0].game_id == 1
    assert result[0].name == "Magic"
    assert result[0].display_name == "Magic: the Gathering"
