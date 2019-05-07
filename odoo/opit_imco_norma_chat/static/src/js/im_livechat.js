/**
 * @file Modificación de livechat odoo para el proyecto NORMA
 * @author Uriel Curiel <uriel@opit.mx>
 * @version 2.1
 * @copyright [OPIT 2018]{@link http://opit.mx}
 */

/**
 * @namespace im_livechat
 */

odoo.define('im_livechat.im_livechat', function(require) {
	"use strict";

	// Librerias requeridas
	var local_storage = require('web.local_storage');
	var bus = require('bus.bus').bus;
	var config = require('web.config');
	var core = require('web.core');
	var session = require('web.session');
	var time = require('web.time');
	var utils = require('web.utils');
	var Widget = require('web.Widget');
	var ChatWindow = require('mail.ChatWindow');

	var _t = core._t;
	var QWeb = core.qweb;

	// Constantes
	var LIVECHAT_COOKIE_HISTORY = 'im_livechat_history';
	var HISTORY_LIMIT = 15;

	// Seguimiento de historial
	var page = window.location.href.replace(/^.*\/\/[^\/]+/, '');
	var page_history = utils.get_cookie(LIVECHAT_COOKIE_HISTORY);
	var url_history = [];
	var opening_chat = false;
	var welcome = true;
	if (page_history) {
		url_history = JSON.parse(page_history) || [];
	}
	if (!_.contains(url_history, page)) {
		url_history.push(page);
		while (url_history.length > HISTORY_LIMIT) {
			url_history.shift();
		}
		utils.set_cookie(LIVECHAT_COOKIE_HISTORY, JSON.stringify(url_history), 60 * 60 * 24); // 1 day cookie
	}
	/**
	 * Botón inicial del chat (animacón de norma)
	 * @version 1.0
	 * @exports im_livechat.chat
	 * @namespace
	 * @property {Object} events - diccionario {evento del mause : función callback}
	 */
	var LivechatButton = Widget.extend({
		className: "openerp o_livechat_button hidden-print",

		events: {
			"click": "open_chat"
		},
		/**
		 * Inicializa el widget del botón inicial de norma
		 *
		 * @memberof im_livechat.chat
		 * @method init
		 * @param {Widget} parent - widget del que hereda.
		 * @param {String} server_url - url al que se hacen las consultas rpc.
		 * @param {Object} options - configuración del chat hecha desde odoo (mensaje inicial,texto del imput, etc.)
		 */
		init: function(parent, server_url, options) {
			this._super(parent);
			this.options = _.defaults(options || {}, {
				input_placeholder: _t('Pregunta algo ...'),
				default_username: _t("Visitante"),
				button_text: _t("Platica con uno de nuestros colaboradores"),
				default_message: _t("¿Cómo te puedo ayudar?"),
			});
			this.channel = null;
			this.chat_window = null;
			this.messages = [];
			this.server_url = server_url;
		},
		/**
		 * Antes de mostrar el botón de norma, verifica si ya se inicio anterior mente una sesión
		 * @memberof im_livechat.chat
		 * @method willStart
		 */
		willStart: function() {
			var self = this;
			var cookie = utils.get_cookie('im_livechat_session');
			var ready;
			if (!cookie) {
				ready = session.rpc("/im_livechat/init", {
					channel_id: this.options.channel_id
				}).then(function(result) {
					if (!result.available_for_me) {
						return $.Deferred().reject();
					}
					self.rule = result.rule;
				});
			} else {
				var channel = JSON.parse(cookie);
				console.log(channel.uuid);
				ready = session.rpc("/mail/chat_history", {
					uuid: channel.uuid,
					limit: 100
				}).then(function(history) {
					self.history = history;
				});
			}
			return ready.then(this.load_qweb_template.bind(this));
		},
		/**
		 * si ya hay una sesión iniciada, muestra la ventana del chat abierta, sino,renderiza la animación de Norma
		 * @memberof im_livechat.chat
		 * @method start
		 */
		start: function() {
			//var html = '<img src="http://admin.imco.opit.mx/opit_imco_norma_chat/static/src/img/norma.svg" alt=""><p>' + this.options.button_text + '</p>';
			//this.$el.html(html)
			this.$el.text(this.options.button_text);
			var small_screen = config.device.size_class === config.device.SIZES.XS;
			if (this.history) {
				_.each(this.history.reverse(), this.add_message.bind(this));
				this.open_chat();
			} else if (!small_screen && this.rule.action === 'auto_popup') {
				var auto_popup_cookie = utils.get_cookie('im_livechat_auto_popup');
				if (!auto_popup_cookie || JSON.parse(auto_popup_cookie)) {
					this.auto_popup_timeout = setTimeout(this.open_chat.bind(this), this.rule.auto_popup_timer * 1000);
				}
			}
			bus.on('notification', this, function(notifications) {
				var self = this;
				_.each(notifications, function(notification) {
					self._on_notification(notification);
				});
			});
			return this._super();
		},
		/**
		 * cuando hay una notificación del servidor
		 * @memberof im_livechat.chat
		 * @method on_notification
		 */
		_on_notification: function(notification) {
			if (this.channel && (notification[0] === this.channel.uuid)) {
				if (notification[1]._type === "history_command") { // history request
					var cookie = utils.get_cookie(LIVECHAT_COOKIE_HISTORY);
					var history = cookie ? JSON.parse(cookie) : [];
					session.rpc("/im_livechat/history", {
						pid: this.channel.operator_pid[0],
						channel_uuid: this.channel.uuid,
						page_history: history,
					});
				} else { // normal message
					this.add_message(notification[1]);
					this.render_messages();
					if (this.chat_window.folded || !this.chat_window.thread.is_at_bottom()) {
						this.chat_window.update_unread(this.chat_window.unread_msgs + 1);
					}
				}
			}
		},
		/**
		 * carga los templates que se ocupan en el widget, estos tambien deben estar definidos en el __manifest__.py del modulo de odoo
		 * @memberof im_livechat.chat
		 * @method load_qweb_template
		 */
		load_qweb_template: function() {
			var xml_files = [
				'/mail/static/src/xml/chat_window.xml',
				'/mail/static/src/xml/thread.xml',
				'/opit_imco_norma_chat/static/xml/norma_livechat.xml',
				'/opit_imco_norma_chat/static/xml/send_transcription.xml',
				'/opit_imco_norma_chat/static/xml/close_livechat.xml',
			];
			var defs = _.map(xml_files, function(tmpl) {
				return session.rpc('/web/proxy/load', {
					path: tmpl
				}).then(function(xml) {
					QWeb.add_template(xml);
				});
			});
			return $.when.apply($, defs);
		},
		/**
		 * inicia el chat
		 * @memberof im_livechat.chat
		 * @method open_chat
		 */
		open_chat: _.debounce(function() {
			var self = this;
			var cookie = utils.get_cookie('im_livechat_session');
			var def;
			opening_chat = true;

			clearTimeout(this.auto_popup_timeout);
			if (cookie) {
				def = $.when(JSON.parse(cookie));
			} else {
				this.messages = []; // re-initialize messages cache
				def = session.rpc('/im_livechat/norma/chat/get_session', {
					channel_id: this.options.channel_id,
					anonymous_name: this.options.default_username,
				}, {
					shadow: true
				});
			}
			def.then(function(channel) {
				if (!channel || !channel.operator_pid) {
					alert(_t("None of our collaborators seems to be available, please try again later."));
				} else {
					self.channel = channel;
					self.open_chat_window(channel);
					if (welcome) {
						self.send_welcome_message();
						welcome = false;
					}
					self.render_messages();

					bus.add_channel(channel.uuid);
					bus.start_polling();

					utils.set_cookie('im_livechat_session', JSON.stringify(channel), 60 * 60);
					utils.set_cookie('im_livechat_auto_popup', JSON.stringify(false), 60 * 60);
				}
			}).always(function() {
				opening_chat = false;
			});
		}, 200, true),

		/**
		 * muestra la ventana del chat
		 * @memberof im_livechat.chat
		 * @method open_chat_window
		 */
		open_chat_window: function(channel, is_open) {
			var self = this;

			var options = {
				display_stars: false,
				placeholder: this.options.input_placeholder || "",
			};
			var is_folded = (channel.state === 'folded');

			this.chat_window = new ChatWindow(this, channel.id, channel.name, is_folded, channel.message_unread_counter, options);
			if ($('.o_chat_window ').length != 0) {

				$('.o_chat_window ').remove();
			}
			this.chat_window.appendTo($('body')).then(function() {
				self.chat_window.$el.css({
					right: 0,
					bottom: 0,
				});
				self.chat_window.$el.fadeIn('slow', function() {

				});
				self.$el.fadeOut('slow', function() {

				});
			});
			var window_c = utils.get_cookie('window');
			console.log(window_c);
			if (window_c) {
				if (window_c === 'close') {
					this.close_chat();
					//this.ask_close()
				} else if (window_c === 'transcription') {
					this.ask_send_trascription()
				} else if (window_c === 'feedback') {
					this.ask_feedback()
				}
			}
			this.chat_window.on("close_chat_session", this, function() {
				var input_disabled = this.chat_window.$(".o_chat_composer input").prop('disabled');
				var ask_fb = !input_disabled && _.find(this.messages, function(msg) {
					return msg.id !== '_welcome';
				});
				if (ask_fb) {
					this.chat_window.toggle_fold(false);
					this.close_chat();
					//this.ask_close();
				} else {
					this.close_chat();
				}
			});
			this.chat_window.on("post_message", this, function(message) {
				// console.log('waiting_message');
				$('.o_thread_message').last().after('<div class="o_thread_message " data-message-id="_welcome" id="waiting_message">' +
					'<div class="o_thread_message_sidebar">' +
					'<img data-oe-model="res.partner" src="http://norma.opit.mx/assets/img/logos/avatar_norma.png" data-oe-id="" class="o_thread_message_avatar img-circle ">' +
					'</div>' +
					'<div class="o_thread_message_core">' +
					'<p class="o_mail_info">' +
					'<strong data-oe-model="res.partner" data-oe-id="" class="o_thread_author ">' +
					'Norma: La abogada de las víctimas' +
					'</strong> - <small class="o_mail_timestamp" title="01/18/2018 18:48:11">now</small>' +
					'<span class="o_thread_icons">' +
					'</span>' +
					'</p>' +
					'<div class="o_thread_message_content">' +
					'<svg version="1.1" id="L4" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 100 50" enable-background="new 0 0 0 0" xml:space="preserve"> <circle fill="#53d4f1" stroke="none" cx="6" cy="25" r="6"> <animate attributeName="opacity" dur="1s" values="0;1;0" repeatCount="indefinite" begin="0.1"/> </circle> <circle fill="#53d4f1" stroke="none" cx="26" cy="25" r="6"> <animate attributeName="opacity" dur="1s" values="0;1;0"' + 'repeatCount="indefinite" begin="0.2"/> </circle> <circle fill="#53d4f1" stroke="none" cx="46" cy="25" r="6"> <animate attributeName="opacity" dur="1s" values="0;1;0" repeatCount="indefinite" begin="0.3"/> </circle> </svg>' +
					'</div>' +
					'</div>' +
					'</div>');
				self.chat_window.thread.scroll_to();
				self.send_message(message).fail(function(error, e) {
					e.preventDefault();
					return self.send_message(message); // try again just in case
				});
			});
			this.chat_window.on("fold_channel", this, function() {
				this.channel.state = (this.channel.state === 'open') ? 'folded' : 'open';
				utils.set_cookie('im_livechat_session', JSON.stringify(this.channel), 60 * 60);
			});
			this.chat_window.thread.$el.on("scroll", null, _.debounce(function() {
				if (self.chat_window.thread.is_at_bottom()) {
					self.chat_window.update_unread(0);
				}
			}, 100));
		},

		/**
		 * minimiza la ventana del chat
		 * @memberof im_livechat.chat
		 * @method close_chat
		 */
		close_chat: function() {
			var self = this;
			opening_chat = true;
			self.$el.fadeIn('slow', function() {

			});
			self.chat_window.$el.fadeOut('slow', function() {
				self.chat_window.folded = false;
			}).animate({
				height: '400px'
			}, 200);
			// utils.set_cookie('im_livechat_session', "", -1); // remove cookie
		},

		/**
		 * manda el mensaje al servidor
		 * @memberof im_livechat.chat
		 * @method send_message
		 */
		send_message: function(message) {
			var self = this;
			return session
				.rpc("/mail/chat_post", {
					uuid: this.channel.uuid,
					message_content: message.content
				})
				.then(function() {
					$('#waiting_message').remove();
					self.chat_window.thread.scroll_to();
				});
		},

		/**
		 * verifica si el menaje es de finalizacion y agrega el mensaje al historico de mensajes
		 * @memberof im_livechat.chat
		 * @method add_message
		 */
		add_message: function(data, options) {
			var re = /((;{3})+(fin)+(;{3}))/g; //codigo para salir (;;;fin;;;)

			if (re.test(data.body)) {
				data.body = data.body.replace(re, '');
				// console.log(message);
				this.ask_send_trascription('add_message', data.body);
			}
			var msg = {
				id: data.id,
				attachment_ids: data.attachment_ids,
				author_id: data.author_id,
				body: data.body,
				date: moment(time.str_to_datetime(data.date)).locale('es-us'),
				is_needaction: false,
				is_note: data.is_note,
				customer_email_data: []
			};

			// Compute displayed author name or email
			msg.displayed_author = msg.author_id && msg.author_id[1] ||
				this.options.default_username;

			// Compute the avatar_url
			msg.avatar_src = this.server_url;
			if (msg.author_id && msg.author_id[0]) {
				//msg.avatar_src += "/web/image/res.partner/" + msg.author_id[0] + "/image_small";
				msg.avatar_src = "http://norma.opit.mx/assets/img/logos/avatar_norma.png";
			} else {
				msg.avatar_src = "http://norma.opit.mx/assets/img/logos/avatar_anonimo.png";
				msg.id = "visit";
			}

			if (options && options.prepend) {
				this.messages.unshift(msg);
			} else {
				this.messages.push(msg);
			}
		},


		/**
		 * renderiza el los mensajes y hace scroll al último
		 * @memberof im_livechat.chat
		 * @method render_messages
		 */
		render_messages: function() {
			var should_scroll = !this.chat_window.folded && this.chat_window.thread.is_at_bottom();
			this.chat_window.render(this.messages);
			if (should_scroll) {
				this.chat_window.thread.scroll_to();
			}
		},

		/**
		 * crea el mensaje de bienvenida
		 * @memberof im_livechat.chat
		 * @method send_welcome_message
		 */
		send_welcome_message: function() {
			if (this.options.default_message) {
				this.add_message({
					id: '_welcome',
					attachment_ids: [],
					author_id: this.channel.operator_pid,
					body: this.options.default_message,
					channel_ids: [this.channel.id],
					date: time.datetime_to_str(new Date()),
					tracking_value_ids: [],
				}, {
					prepend: true
				});
			}
		},

		/**
		 * muestra una ventana con tres acciones (minimizar,continuar,cerrar)
		 * @memberof im_livechat.chat
		 * @method ask_close
		 */
		ask_close: function() {
			utils.set_cookie('window', "close", 60 * 60 * 24);
			var self = this
			this.chat_window.$(".o_chat_composer input").prop('disabled', true);

			this.closeQuestion = new CloseQuestion(this, this.channel.uuid);
			this.closeQuestion.replace(this.chat_window.thread.$el);

			this.closeQuestion.on("continue_chat", this, function() {
				console.log(opening_chat);
				self.open_chat();
				this.chat_window.$(".o_chat_composer input").prop('disabled', false);
			});
			this.closeQuestion.on("min_chat", this, function() {
				self.open_chat();
				self.chat_window.$(".o_chat_composer input").prop('disabled', false);
				self.chat_window.$(".o_chat_title").trigger('click');

				if ($('header').width() <= 768) {
					self.close_chat();
				}
			});
			this.closeQuestion.on("close_chat", this, function() {
				this.ask_send_trascription('close', '___________________');
			});
		},

		/**
		 * mauestra ventana con la recomendación y el campo para el email
		 * @memberof im_livechat.chat
		 * @method ask_send_trascription
		 */
		ask_send_trascription: function(prev, message) {
			var c = utils.get_cookie("window");
			if (!c) {
				utils.set_cookie('window', "transcription", 60 * 60 * 24); // remove cookie

			}
			// console.log(prev);
			message = message || '';
			// console.log(message);
			// console.log(this);
			this.send_trascription = new SendTranscription(this, this.channel.uuid, message);
			if (this.chat_window) {
				this.chat_window.$(".o_chat_composer input").prop('disabled', true);

				if (prev === 'close')
					this.send_trascription.replace(this.closeQuestion.$el);
				else {
					this.send_trascription.replace(this.chat_window.thread.$el);

				}
			}
			this.send_trascription.on("close_chat", this, function() {
				this.ask_feedback();
			});
		},
		/**
		 * mauestra ventana con los botones de feedback (bueno,regular,malo)
		 * @memberof im_livechat.chat
		 * @method ask_feedback
		 */
		ask_feedback: function() {
			utils.set_cookie('window', "feedback", 60 * 60 * 24); // remove cookie
			var feedback = new Feedback(this, this.channel.uuid);
			if (this.send_trascription) {
				feedback.replace(this.send_trascription.$el);
			} else {
				feedback.replace(this.chat_window.thread.$el);
			}

			feedback.on("send_message", this, this.send_message);
			feedback.on("feedback_sent", this, function() {
				this.close_chat();
				location.reload();
			});
		}
	});
	/**
	 * Widget de la ventana con las acciones de minimizar, continuar o cerrar
	 * @version 1.0
	 * @exports im_livechat.closeQuestion
	 * @namespace
	 * @property {string} template - template xml que va a renderizar el widget
	 * @property {Object} events - diccionario {evento del mause : función callback}
	 */
	var CloseQuestion = Widget.extend({
		template: "opit_livechat.closeChat",
		events: {
			'click .o_livechat_close_btn.seguir': 'on_continue_chat',
			'click .o_livechat_close_btn.min': 'on_min_chat',
			'click .o_livechat_close_btn.cerrar': 'on_close_chat',
		},
		/**
		 * metodo constructor del widget
		 * @memberof im_livechat.closeQuestion
		 * @method init
		 * @param {Widget} parent - widget del que hereda
		 * @param {Widget} channel_uuid - canal del chat usado
		 */
		init: function(parent, channel_uuid) {
			this._super(parent);
			this.channel_uuid = channel_uuid;
			this.server_origin = session.origin;
		},
		/**
		 * callback para continuar con el chat
		 * @memberof im_livechat.closeQuestion
		 * @method on_continue_chat
		 */
		on_continue_chat: function() {
			this.trigger('continue_chat');
			console.log('continuar');
			return true;
		},
		/**
		 * callback para minimizar el chat
		 * @memberof im_livechat.closeQuestion
		 * @method ask_send_trascription
		 */
		on_min_chat: function() {
			this.trigger('min_chat');
			console.log('min');
			return true;
		},
		/**
		 * callback para cerrar el chat
		 * @memberof im_livechat.closeQuestion
		 * @method ask_send_trascription
		 */
		on_close_chat: function() {
			console.log('close');
			this.trigger('close_chat');
			return true;
		}
	});
	/**
	 * Widget de la ventana con la recomendación de norma y el input del email para mandar transcipción
	 * @version 1.0
	 * @exports im_livechat.SendTranscription
	 * @namespace
	 * @property {string} template - template xml que va a renderizar el widget
	 * @property {Object} events - diccionario {evento del mause : función callback}
	 */
	var SendTranscription = Widget.extend({
		template: "opit_livechat.transcriptionChat",
		events: {
			'click .o_livechat_transcription_btn.send': 'on_send_chat',
			'click .o_livechat_transcription_btn.skip': 'on_close_chat',
		},
		init: function(parent, channel_uuid, message) {
			this._super(parent);
			this.channel_uuid = channel_uuid;
			this.server_origin = session.origin;
			this.message = message ||utils.get_cookie('recomendation')||'';
			utils.set_cookie('recomendation',this.message,60*60);
		},
		/**
		 * renderiza la recomendación de norma en la ventana
		 * @memberof im_livechat.SendTranscription
		 * @method start
		 */
		start: function() {

			this.$('.o_livechat_recommendation').html($.trim(this.message))
		},
		/**
		 * callback para mandar el email
		 * @memberof im_livechat.SendTranscription
		 * @method on_send_chat
		 */
		on_send_chat: function() {
			var re = /[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/g;
			this.$('.help-block').addClass('hidden');
			this.$('#emailForm').removeClass('has-error');
			var sEmail = this.$('#InputEmail').val();
			if ($.trim(sEmail).length == 0) {
				this.$('#emailForm').addClass('has-error');
				this.$('.help-block.empty').removeClass('hidden');

			} else if (re.test(sEmail)) {
				this.$('#emailForm').removeClass('has-error');
				var cookie = utils.get_cookie('im_livechat_session');
				var channel = JSON.parse(cookie);
				var self = this;
				session.rpc("/mail/chat_post", {
						uuid: this.channel_uuid,
						message_content: sEmail,
					})
					.then(function() {
						session.rpc("/mail/chat_history", {
							uuid: channel.uuid,
							limit: 100
						}).then(function(history) {
							var re_res = /((;{3})+(calificacion)+(;{3}))/g; //codigo para salir (;;;calificacion;;;)
							if (re_res.test(history[0].body)) {
								self.trigger('close_chat');
							}
						});
					});
			} else {
				this.$('#emailForm').addClass('has-error');
				this.$('.help-block.invalid').removeClass('hidden');
			}

			return true;
		},
		/**
		 * callback para in a la ventana de feedback
		 * @memberof im_livechat.SendTranscription
		 * @method on_close_chat
		 */
		on_close_chat: function() {
			console.log('close');
			this.trigger('close_chat');
			return true;
		}
	});

	/**
	 * Este widget muestra 3 niveles de rating
	 * @version 1.0
	 * @exports im_livechat.feedback
	 * @namespace
	 * @property {string} template - template xml que va a renderizar el widget
	 * @property {Object} events - diccionario {evento del mause : función callback}
	 */
	var Feedback = Widget.extend({
		template: "norma_livechat.FeedBack",

		events: {
			'click .o_livechat_rating_choices .o_livechat_img': 'on_click_smiley',
			'click .o_livechat_no_feedback em': 'on_click_no_feedback',
			'click .o_rating_submit_button': 'on_click_send',
			'click .o_livechat_send_button .btn': 'on_send_feedback'
		},
		/**
		 * constructor del widget
		 * @memberof im_livechat.feedback
		 * @method init
		 */
		init: function(parent, channel_uuid) {
			this._super(parent);
			this.channel_uuid = channel_uuid;
			this.server_origin = session.origin;
			this.rating = undefined;


		},
		/**
		 * oculta el boton de envio de feedback
		 * @memberof im_livechat.feedback
		 * @method start
		 */
		start: function() {
			this.$el.children('.o_livechat_send_button').hide();
		},

		/**
		 * callback al dar click en un nivel de rating, resalta el nivel al que se dio click
		 * @memberof im_livechat.feedback
		 * @method on_click_smiley
		 */
		on_click_smiley: function(ev) {
			this.rating = parseInt($(ev.currentTarget).data('value'));
			this.$('.o_livechat_rating_choices .o_livechat_img').removeClass('selected');
			this.$('.o_livechat_rating_choices .o_livechat_img[data-value="' + this.rating + '"]').addClass('selected');

			// only display textearea if bad smiley selected
			var close_chat = false;
			if (this.rating === 0) {
				this.$('.o_livechat_rating_reason').show();
			} else {
				this.$('.o_livechat_rating_reason').hide();
				close_chat = true;
			}
			if (this.rating != undefined) {
				this.$('.o_livechat_send_button').show();
			}
			//Cerramos el chat despues de seleccionar una calificacion
			this._send_feedback({close: true});
		},
		/**
		 * callback para mandar el feedback
		 * @memberof im_livechat.feedback
		 * @method on_send_feedback
		 */
		on_send_feedback: function() {
			this._send_feedback({
				close: true
			});
		},
		/**
		 * callback para cerrar el chat sin mandar feedback
		 * @memberof im_livechat.feedback
		 * @method on_click_no_feedback
		 */
		on_click_no_feedback: function() {
			this.trigger("feedback_sent"); // will close the chat
		},
		/**
		 * callback para mandar un comentario además del nivel de rating
		 * @memberof im_livechat.feedback
		 * @method on_click_send
		 */
		on_click_send: function() {
			if (_.isNumber(this.rating)) {
				this._send_feedback({
					reason: this.$('textarea').val(),
					close: true
				});
			}
		},
		/**
		 * función para mandar el feedback al servidor de odoo
		 * @memberof im_livechat.feedback
		 * @method _send_feedback
		 */
		_send_feedback: function(options) {
			var self = this;
			var args = {
				uuid: this.channel_uuid,
				rate: this.rating,
				reason: options.reason
			};
			return session.rpc('/im_livechat/feedback', args).then(function() {
				if (options.close) {
					var content = _.str.sprintf(_t("Rating: :rating_%d"), self.rating);
					if (options.reason) {
						content += " \n" + options.reason;
					}
					// self.trigger("send_message", {
					// 	content: content
					// });
					self.trigger("feedback_sent"); // will close the chat
					// termina el chat
					utils.set_cookie('im_livechat_session', "", -1); // remove cookie
					utils.set_cookie('window', "", -1); // remove cookie
					opening_chat = false;

				}
			});
		}
	});

	return {
		LivechatButton: LivechatButton,
		CloseQuestion: CloseQuestion,
		Feedback: Feedback,
	};

});