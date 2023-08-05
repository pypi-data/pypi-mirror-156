__version__ = '0.8.41'

from .getter import Getter
from .core import App, Security

# backward compatible
SwaggerApp = App
SwaggerSecurity = Security
SwaggerAuth = SwaggerSecurity

