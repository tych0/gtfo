from web import form

_validators = [
  form.Validator("name is required!", lambda i: i.name),
  form.Validator("payload is required!", lambda i: i.payload),
]

reply_form = form.Form(form.Textbox('name'),
                       form.Textbox('url'),
                       form.Textbox('email'),
                       form.Textarea('payload'),
                       validators = _validators
                      )
