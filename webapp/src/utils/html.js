var htmlEscapable = /[&<>"'/]/g;
var htmlEscaped = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#x27;',
  '/': '&#x2F;'
};

export default {
  escape(html) {
    return html.replace(htmlEscapable, function(match) {
      return htmlEscaped[match];
    });
  }
};
