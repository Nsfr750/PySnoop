{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :show-inheritance:
   :undoc-members:
   :special-members: __init__
   :inherited-members:
   
   .. rubric:: Methods Summary
   
   .. autosummary::
      :toctree: _autosummary
      :template: custom-module-template.rst
      :recursive:
      
      {% for item in methods %}
      ~{{ name }}.{{ item }}
      {%- endfor %}
   
   .. rubric:: Attributes Summary
   
   .. autosummary::
      :toctree: _autosummary
      :template: custom-module-template.rst
      :recursive:
      
      {% for item in attributes %}
      ~{{ name }}.{{ item }}
      {%- endfor %}
