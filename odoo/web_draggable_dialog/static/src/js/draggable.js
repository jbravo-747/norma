//-*- coding: utf-8 -*-
//############################################################################
//
//   This module Copyright (C) 2018 MAXSNS Corp (http://www.maxsns.com)
//   Author: Henry Zhou (zhouhenry@live.com)
//
//   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
//   OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
//   THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
//   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
//   DEALINGS IN THE SOFTWARE.
//
//############################################################################

odoo.define('web_draggable_dialog', function (require) {
'use strict';

var Dialog = require('web.Dialog');

Dialog.include({
    opened: function (handler) {
        var self = this;
        return this._super(handler).done(function() {
            var draggable = self.$modal.draggable('instance');
                if (!draggable) {
                self.$modal.draggable({
                    handle: '.modal-header',
                    helper: false
                });
            }
        });
    },
});

});