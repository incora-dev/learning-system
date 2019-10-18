$(function () {

    $('#loading').remove();

    /*
     * Popups messages and dialogs (magnificPopup)
     */

    $('.send_message').magnificPopup({
        mainClass: 'my-mfp-zoom-in'
    });

    $('.popupnotif').magnificPopup({
        mainClass: 'my-mfp-zoom-in'
    });

    $('.del-dialog').magnificPopup({
        mainClass: 'my-mfp-zoom-in'
    });

    $('.note-delete-icon').magnificPopup({
        mainClass: 'my-mfp-zoom-in'
    });

    $('.note-edit-icon').magnificPopup({
        mainClass: 'my-mfp-zoom-in'
    });

    /*
     * Update page select: custom or image
     */

    if ($('#id_pagetype').val() === "image") {
        $('label:contains("Pagetype:")').empty();
        $("#id_pagetype").addClass('hidden');
        $("#custom_content").addClass('hidden');
        $("#image_file_reference").removeClass('hidden');
        $("#sort_index").removeClass('hidden');
    }
    if ($('#id_pagetype').val() === "custom") {
        $('label:contains("Pagetype:")').empty();
        $("#id_pagetype").addClass('hidden');
        $("#custom_content").removeClass('hidden');
        $("#image_file_reference").addClass('hidden');
        $("#sort_index").addClass('hidden');
    }

    $('#id_pagetype').change(function () {
        if ($(this).val() === "image") {
            $('label:contains("Pagetype:")').empty();
            $("#id_pagetype").addClass('hidden');
            $("#custom_content").addClass('hidden');
            $("#image_file_reference").removeClass('hidden');
            $("#sort_index").removeClass('hidden');
        }
        if ($(this).val() === "custom") {
            $('label:contains("Pagetype:")').empty();
            $("#id_pagetype").addClass('hidden');
            $("#custom_content").removeClass('hidden');
            $("#image_file_reference").addClass('hidden');
            $("#sort_index").addClass('hidden');
        }
    });

    /*
     * Change style btn input type=file:
     */

    if ($('#chose_file').length) {
        $('#chose_file').click(function () {
            $('#chose_file_input').click();
            return (false);
        });

        $('#chose_file_input').change(function () {
            $('#chose_file_text').html($(this).val());

        }).change();
    }

    $('.cfile_wrapp').replaceAll('#id_pdf_file');
    $('.cfile_wrapp').replaceAll('#id_icon');

    /*
     * Popup notification on changes (with close delay):
     */

    if ($('#notification').html().length > 15) {
        $('.popupnotif').click();
        setTimeout(function () {
            $('.mfp-close-ok').click();
        }, 2000);
    } else {
    }


    /*
     * Delete default checkbox and label in choose icon
     */

    $('#icon-clear_id').remove();
    $('[for = "icon-clear_id"]').remove();


    /*
     * Open fix position for student:
     */

    if ($("div").is(".edit-icon")) {
    } else {
        $(".open-btn").css("margin-top", "14px");
    }

    if ($("h2").is(".mod-title-st")) {
        $(".course-controls").css("margin-top", "138px");
    }

    /*
     * Custom notifications:
     */

    //Generate all saved dots:
    var allDots = $('[data-coord]');

    for (i = 0; i < allDots.length; i++) {
        var coordY = allDots[i].getAttribute('data-coord');
        $(".dots").append(`<div class="note-point animationAp" style="margin-top:${coordY - 327}px"></div>`);
    }

    //Create dot:
    $("#documentField").click(function (e) {
        $(".new-dot").remove();
        console.log(e.pageY);
        $(".dots").append(`<div class="note-point animationAp new-dot" style="margin-top:${e.pageY - 327}px"></div>`);
        // $("#inputNote").attr('data-coord', e.pageY);
        $("#inputCoord").val(e.pageY);

        //Remove all prev background for notes:
        $(".activeNote").removeClass('activeNote');

        //Remove all prev background for dots:
        for (i = 0; i < $(".note-point").length; i++) {
            $(".note-point")[i].style.backgroundColor = "#fff";
        }

        //Change create new mod:
        $("#inputBtn").removeClass('hidden');
        $("#inputNote").removeClass('hidden');
    });

    //Click on dot:
    $(".dots").click(function (e) {
        //Remove all prev background for notes:
        $(".activeNote").removeClass('activeNote');

        //Remove all prev background for dots:
        for (i = 0; i < $(".note-point").length; i++) {
            $(".note-point")[i].style.backgroundColor = "#fff";
        }

        //Pick coords from clicked dot, select current note:
        e.target.style.backgroundColor = "#f6a623";
        var selectedCoord = e.target.offsetTop + 327;
        $(".notes-list").find("[data-coord='" + selectedCoord + "']").addClass('activeNote');

        //Change create new mod:
        $(".new-dot").remove();
        $("#inputBtn").addClass('hidden');
        $("#inputNote").addClass('hidden');
    });

    //Click on note:
    $(".cust-note").click(function (e) {
        //Remove all prev background for notes:
        $(".activeNote").removeClass('activeNote');

        //Remove all prev background for dots:
        for (i = 0; i < $(".note-point").length; i++) {
            $(".note-point")[i].style.backgroundColor = "#fff";
        }

        if (e.target.getAttribute('data-coord')) {
            $(e.target).addClass("activeNote");
            var newCoord = e.target.getAttribute('data-coord');
            var allPoints = $(".note-point");
            for (i = 0; i < allPoints.length; i++) {
                 if ($(".note-point")[i].offsetTop + 327 === +newCoord) {
                     $(".note-point")[i].style.backgroundColor = "#f6a623";
                 }
            }
        } else if (e.target.getAttribute('data-coord') === null){
            $(e.target).parent().parent().addClass("activeNote");
            var newCoord = $(e.target).parent().parent()[0].getAttribute('data-coord');
            var allPoints = $(".note-point");
            for (i = 0; i < allPoints.length; i++) {
                if ($(".note-point")[i].offsetTop + 327 === +newCoord) {
                    $(".note-point")[i].style.backgroundColor = "#f6a623";
                }
            }
        }

        //Change create new mod:
        $(".new-dot").remove();
        $("#inputBtn").addClass('hidden');
        $("#inputNote").addClass('hidden');
    });

    /*
     * Editing custom notifications:
     */

});
