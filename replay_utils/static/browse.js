function selectFrame(frame) {
    console.log(frame);
    var img_path =
        '/replay_data/hz' + frame + '.png?no_cache=' + Math.random();
    var log_path =
        '/replay_data/log' + frame + '.txt?no_cache=' + Math.random();

    $.ajax({
        url: log_path,
    }).done(function (data) {
        $('#log').text(data);
    }).fail(function () {
        $('#log').text('error loading logs');
    });

    $('#pic').attr('src', img_path);

    $('#frame' + selected).removeClass('selected');
    selected = frame;
    $('#frame' + frame).addClass('selected');

    window.location.hash = frame;
}

if (window.location.hash) {
    selectFrame(window.location.hash.substring(1));
}


function keydown(e) {
    var keyCode = e.keyCode || e.which;

    var i = frames.indexOf(selected);

    if (keyCode == 40) {
        // up
        if (i + 1 < frames.length)
            selectFrame(frames[i + 1]);
    } else if (keyCode == 38) {
        // down
        if (i > 0)
            selectFrame(frames[i - 1]);
    } else if (keyCode == 36) {
        // home
        selectFrame(frames[0]);
    } else if (keyCode == 35) {
        // end
        selectFrame(frames[frames.length - 1]);
    } else {
        return;
    }
    e.preventDefault();
    e.stopPropagation();
}

$('*').keydown(keydown);
