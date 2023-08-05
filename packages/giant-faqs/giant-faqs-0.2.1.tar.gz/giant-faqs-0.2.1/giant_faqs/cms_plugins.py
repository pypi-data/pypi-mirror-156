from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import FAQBlock


@plugin_pool.register_plugin
class FAQPlugin(CMSPluginBase):
    render_template = "faqs/plugin.html"
    name = "FAQ Block"
    model = FAQBlock
