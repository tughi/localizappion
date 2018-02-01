define(['knockout', 'text!./project-create.html', 'graphql', 'hasher'], function (ko, template, graphql, hasher) {
    'use strict';

    function ViewModel(params) {
        this.name = ko.observable();

        this.createProject = function (self) {
            graphql({
                query: `
                    mutation ($name: String!) {
                        createProject(name: $name) {
                            project {
                                id
                            }
                        }
                    }
                `,
                variables: {
                    name: self.name()
                }
            }).then(result => {
                hasher.setHash(`projects/${result.data.createProject.project.id}`);
            });
        }
    }

    return {
        template,
        viewModel: ViewModel
    };
});

