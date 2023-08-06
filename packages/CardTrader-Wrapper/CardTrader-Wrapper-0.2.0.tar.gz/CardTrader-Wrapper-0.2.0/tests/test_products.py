from cardtrader.service import CardTrader


def test_products_by_expansion(session: CardTrader):
    results = session.products_by_expansion(expansion_id=1)
    result = [x for x in results if x.product_id == 69809122]
    assert len(result) == 1
    assert result[0].quantity == 5
    assert result[0].description == "Magic webshop since 2005!"
    assert result[0].blueprint_id == 49489
    assert result[0].expansion is not None
    assert result[0].graded is None
    assert result[0].product_id == 69809122
    assert result[0].tag is None
    assert result[0].bundle_size == 1
    assert result[0].on_vacation is False
    assert result[0].seller is not None
    assert result[0].name == "Bone Splinters"
    assert result[0].price is not None
    assert result[0].properties is not None


def test_products_by_blueprint(session: CardTrader):
    results = session.products_by_blueprint(blueprint_id=1)
    result = [x for x in results if x.product_id == 127886155]
    assert len(result) == 1
    assert result[0].quantity == 1
    assert result[0].description == "TBS #1"
    assert result[0].blueprint_id == 1
    assert result[0].expansion is not None
    assert result[0].graded is None
    assert result[0].product_id == 127886155
    assert result[0].tag is None
    assert result[0].bundle_size == 1
    assert result[0].on_vacation is False
    assert result[0].seller is not None
    assert result[0].name == "Rampaging Brontodon"
    assert result[0].price is not None
    assert result[0].properties is not None
