@api.model
def _update_user_groups_view(self):
	""" Modify the view with xmlid ``base.user_groups_view``, which inherits
					the user form view, and introduces the reified group fields.
	"""
	print('___________________________ update groups _______________________________')
	if self._context.get('install_mode'):
		# use installation/admin language for translatable names in the view
		user_context = self.env['res.users'].context_get()
		self = self.with_context(**user_context)

	# We have to try-catch this, because at first init the view does not
	# exist but we are already creating some basic groups.
	view = self.env.ref('base.user_groups_view', raise_if_not_found=False)
	if view and view.exists() and view._name == 'ir.ui.view':
		group_no_one = view.env.ref('base.group_no_one')
		xml1, xml2 = [], []
		xml1.append(E.separator(
			string=_('Application Accesses'), colspan="2"))
		tree = etree.Element("div")
		tree.set('class', 'accordion')
		n = 0
		for app, kind, gs in self.get_groups_by_application():
			# hide groups in categories 'Hidden' and 'Extra' (except for group_no_one)
			attrs = {}
			if app.xml_id in ('base.module_category_hidden', 'base.module_category_extra', 'base.module_category_usability'):
				attrs['groups'] = 'base.group_no_one'

			if kind == 'selection':
				# application name with a selection field
				field_name = name_selection_groups(gs.ids)
				xml1.append(E.field(name=field_name, **attrs))
				xml1.append(E.newline())
			else:
				# application separator with boolean fields
				app_name = app.name or _('Other')
				app_id = n
				# xml2.append(E.separator(string=app_name, colspan="4", **attrs))
				tab = etree.Element('div', **attrs)
				tab.set('class', "tab")
				tab.append(etree.Element('input', id='tab-' + str(app_id), name="tabs", type="checkbox"))
				label = etree.Element('label', string=app_name)
				label.set('for', 'tab-' + str(app_id))

				tab.append(label)
				content = etree.Element('div')
				content.set('class', "tab-content")
				for g in gs:
					field_name = name_boolean_group(g.id)
					group_name = g.name

					if g == group_no_one:
						# make the group_no_one invisible in the form view
						#xml2.append(E.field(name=field_name, invisible="1", **attrs))
						formControl = etree.Element('div')
						formControl.append(
							E.field(name=field_name, id=field_name, invisible="1", **attrs))
						label = etree.Element('label', string=group_name,invisible="1")
						label.set('for', field_name)
						formControl.append(label)
						content.append(formControl)
					else:
						# xml2.append(E.field(name=field_name, **attrs))
						formControl = etree.Element('div')
						formControl.append(
								E.field(name=field_name, id=field_name, **attrs))
						label = etree.Element('label', string=group_name)
						label.set('for', field_name)
						formControl.append(label)
						content.append(formControl)
					tab.append(content)
				tree.append(tab)
				n = n + 1
		xml2.append(tree)
		# print(etree.tostring(tree,pretty_print=True));
		xml2.append({'class': "o_label_nowrap"})
		xml = E.field(E.group(*(xml1), col="2"), E.group(*(xml2),
														 col="4"), name="groups_id", position="replace")
		xml.addprevious(etree.Comment("GENERATED AUTOMATICALLY BY GROUPS"))
		xml_content = etree.tostring(
			xml, pretty_print=True, encoding="unicode")
		# print(xml_content)
		view.with_context(lang=None).write(
			{'arch': xml_content, 'arch_fs': False})
