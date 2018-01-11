var Localizappion = {}

function graphql(options) {
    var query = options.query;
    var variables = options.variables;
    return $.post('graphql', { query, variables: JSON.stringify(variables) });
}