$(document).ready(() => {
    /* global tableSkilllist */
    /* global MaDCSettings */
    const modalRequestApprove = $('#skillplan-delete');

    // Approve Request Modal
    modalRequestApprove.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');
        const pk = button.data('pk');

        // Extract the title from the button
        const modalTitle = button.data('title');
        const modalTitleDiv = modalRequestApprove.find('#modal-title');
        modalTitleDiv.html(modalTitle);

        // Extract the text from the button
        const modalText = button.data('text');
        const modalDiv = modalRequestApprove.find('#modal-request-text');
        modalDiv.html(modalText);

        $('#modal-button-confirm-delete-request').on('click', () => {
            const form = modalRequestApprove.find('form');
            const pkField = form.find('input[name="pk"]');
            pkField.val(pk);
            const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

            const posting = $.post(
                url,
                {
                    pk: pk,
                    csrfmiddlewaretoken: csrfMiddlewareToken
                }
            );

            posting.done((data) => {
                if (data.success === true) {
                    modalRequestApprove.modal('hide');

                    // Reload with no Modal
                    const skilllistTable = $('#skill-list-table').DataTable();
                    skilllistTable.ajax.reload();
                }
            }).fail((xhr, _, __) => {
                const response = JSON.parse(xhr.responseText);
                const errorMessage = $('<div class="alert alert-danger"></div>').text(response.message);
                form.append(errorMessage);
            });
        });
    }).on('hide.bs.modal', () => {
        modalRequestApprove.find('.alert-danger').remove();
        $('#modal-button-confirm-delete-request').unbind('click');
    });
});
