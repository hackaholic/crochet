import pytest
from pydantic import ValidationError
from app.schemas.storefront import BrandSettingsUpdate, BrandSettingsOut

def test_brand_logo_key_resolves_via_image_configuration():
    value=BrandSettingsUpdate(logoUrl='brand/sulocraft-logo.png')
    assert value.logo_url=='brand/sulocraft-logo.png'
    output=BrandSettingsOut.model_validate({'logo_url':value.logo_url}).model_dump(by_alias=True)
    assert output['logoUrl'].endswith('/brand/sulocraft-logo.png')

@pytest.mark.parametrize('value',['javascript:alert(1)','../secret','/etc/passwd','data:image/png;base64,abc'])
def test_logo_rejects_unsafe_keys(value):
    with pytest.raises(ValidationError): BrandSettingsUpdate(logoUrl=value)
