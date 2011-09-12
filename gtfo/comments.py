from web import form

_validators = [
  form.Validator("name is required!", lambda i: i.name),
  form.Validator("payload is required!", lambda i: i.payload),
  form.Validator("your word is not orange!", lambda i: i.capcha == 'orange'),
]

reply_form = form.Form(form.Textbox('name', description='name (required)'),
                       form.Textbox('capcha', description='type orange in this box:'),
                       form.Textbox('url', description='homepage (optional)'),
                       form.Textbox('email', description='email (optional)'),
                       form.Textarea('payload', cols=40, rows=10),
                       validators = _validators
                      )

