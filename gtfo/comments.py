from web import form

reply_form = form.Form(form.Textbox('name'),
                       form.Textbox('url'),
                       form.Textbox('email'),
                       form.Textarea('payload'),
                      )
