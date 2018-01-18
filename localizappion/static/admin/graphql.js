define(['jquery'], function ($) {
    'use strict';

    return function (options) {
        var query = options.query;
        var variables = options.variables;
        return $.post('graphql', { query, variables: JSON.stringify(variables) });
    }
});
