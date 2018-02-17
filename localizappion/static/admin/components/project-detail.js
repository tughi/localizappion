define(['knockout', 'graphql', 'text!./project-detail.html'], function (ko, graphql, template) {
    'use strict';

    function ViewModel(params) {
        this.allProjects = ko.observable();
        this.project = ko.observable();

        graphql({
            query: `
                query ($projectId: ID!) {
                    project(id: $projectId) {
                        id
                        uuid
                        newSuggestionsCount
                        screenshotsCount
                        stringsCount
                        translations {
                            id
                            language {
                                name
                            }
                            translatedStringsCount
                        }
                    }
                    allProjects: projects {
                        id
                        name
                    }
                }
            `,
            variables: {
                projectId: params.projectId
            }
        }).then(response => {
            this.allProjects(response.data.allProjects);
            this.project(response.data.project);
        });
    }

    return {
        template,
        viewModel: ViewModel
    };
});

