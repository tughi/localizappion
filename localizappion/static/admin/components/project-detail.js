define(['knockout', 'graphql', 'text!./project-detail.html'], function (ko, graphql, template) {
    'use strict';

    function ViewModel(params) {
        this.project = ko.observable();

        graphql({
            query: `
                query ($projectId: ID!) {
                    project(id: $projectId) {
                        uuid
                    }
                }
            `,
            variables: {
                projectId: params.projectId
            }
        }).then(response => {
            this.project(response.data.project);
        });
    }

    return {
        template,
        viewModel: ViewModel
    };
});

