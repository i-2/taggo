from jinja2 import Template

def apply_template(dicty, **kwds):
    """apply templating recursively"""
    new_dicty = dicty.copy()
    for key, value in new_dicty.items():
        if isinstance(value, dict):
            new_dicty[key] = apply_template(value)
        elif isinstance(value, str):
            _template = Template(value)
            new_dicty[key] = _template.render(**kwds)
    return new_dicty