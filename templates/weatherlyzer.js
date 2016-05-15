$(document).ready(function () {

  var SELECTS = ['#year', '#month', '#day', '#hour'];

  var render_graph = function () {

    var graph_req = $.post('{% url 'graph' %}', {
        csrfmiddlewaretoken: '{{ csrf_token }}',
        year: $('#year').val(),
        month: $('#month').val(),
        day: $('#day').val(),
        hour: $('#hour').val(),
        type: $('#type').val(),
        locations: $('#locations').val()
      });

    var data = {
      labels: [],
      datasets: []
    };

    graph_req.done(
      function (response) {

        data.labels = response.deltas;

        $.each(response.table, function (i, item) {
          data.datasets.push({
            label: item.label,
            fill: false,
            borderColor: item.color,
            pointBorderColor: item.color,
            pointBackgroundColor: '#fff',
            data: item.accuracies
          });
        });
      }
    );
  
    graph_req.always(
      function (response) {
        var ctx = document.getElementById('data_chart');
        var data_chart = new Chart(ctx, {
          type: 'line',
          data: data,
          scaleOverride: true,
          scaleSteps: 10,
          scaleStartValue: 0,
          scaleStepWidth: 10,
          options: {
            animation: false,
            scales: {
              yAxes: [{
                scaleLabel: {
                  display: true,
                  labelString: 'Accuracy in %'
                }
              }],
              xAxes: [{
                scaleLabel: {
                  display: true,
                  labelString: 'Delta in hours'
                }
              }]
            }
          }
        });
      }
    );
  };

  var enable_select = function (select_id) {
    $(select_id).prop('disabled', false);
    $(select_id).selectpicker('refresh');
  };

  var disable_selects = function (start_select_id) {
    for (i = SELECTS.indexOf(start_select_id); i < SELECTS.length; i++) {
      $(SELECTS[i]).prop('disabled', true);
      $(SELECTS[i]).val('-1');
      $(SELECTS[i]).selectpicker('refresh');
    }
  };

  var reset_selects = function () {
    for (i = 0; i < SELECTS.length; i++) {
      if (i != 0) {
        $(SELECTS[i]).prop('disabled', true);
      }
      $(SELECTS[i]).val('-1');
    }
  };

  var load_months = function (year) {
    $.post('{% url 'months' %}', {
        csrfmiddlewaretoken: '{{ csrf_token }}',
        year: year
      },
      function (response) {
        $('#month').find('option').remove();
        $('#month').append($('<option>', {
          value: -1,
          text: 'All months'
        }));
        $.each(response.months, function (i, item) {
          $('#month').append($('<option>', {
            value: item.id,
            text: item.name
          }));
        });
        $('#month').selectpicker('refresh');
      });
  };

  var load_days = function (year, month) {
    $.post('{% url 'days' %}', {
        csrfmiddlewaretoken: '{{ csrf_token }}',
        year: year,
        month: month
      },
      function (response) {
        $('#day').find('option').remove();
        $('#day').append($('<option>', {
          value: -1,
          text: 'All days'
        }));
        $.each(response.days, function (i, item) {
          $('#day').append($('<option>', {
            value: item.id,
            text: item.name
          }));
        });
        $('#day').selectpicker('refresh');
      });
  };

  var load_hours = function (year, month, day) {
    $('#hour').find('option').remove();
    $('#hour').append($('<option>', {
      value: -1,
      text: 'All hours'
    }));
    $.post('{% url 'hours' %}', {
        csrfmiddlewaretoken: '{{ csrf_token }}',
        year: year,
        month: month,
        day: day
      },
      function (response) {
        $.each(response.hours, function (i, item) {
          $('#hour').append($('<option>', {
            value: item.id,
            text: item.name
          }));
        });
        $('#hour').selectpicker('refresh');
      });
  };

  var time_select_changed = function (select_id) {
    var nextID = SELECTS[SELECTS.indexOf(select_id) + 1];
    if (nextID != undefined) {
      if ($(select_id).val() == '-1') {
        disable_selects(nextID);
      } else {
        var selected_year = $('#year').val();
        var selected_month = $('#month').val();
        var selected_day = $('#day').val();
        switch (nextID) {
        case '#month':
          load_months(selected_year);
          break;
        case '#day':
          load_days(selected_year, selected_month);
          break;
        case '#hour':
          load_hours(selected_year, selected_month, selected_day);
          break;
        }
        enable_select(nextID);
      }
    }

    render_graph();
  };

  var bind_time_selects_changed = function () {
    for (i = 0; i < SELECTS.length; i++) {
      var _select_changed = time_select_changed.bind(undefined, SELECTS[i]);
      $(SELECTS[i]).change(_select_changed);
    }
  };

  var bind_locations_select_changed = function () {
    $('#locations').change(render_graph);
  };

  var bind_type_select_changed = function () {
    $('#type').change(render_graph);
  };

  reset_selects();
  bind_time_selects_changed();
  bind_locations_select_changed();
  bind_type_select_changed();
  render_graph();
});
