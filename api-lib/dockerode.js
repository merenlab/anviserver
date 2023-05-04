var Docker = require('dockerode');
var docker = new Docker({ socketPath: '/var/run/docker.sock' });

docker.run(
  'meteahaansever/anviserver:latest',
  [],
  process.stdout,
  {
    Volumes: {
      '/anviserver': {},
    },
    ExposedPorts: {
      '80/tcp': {},
    },
    HostConfig: {
      PortBindings: {
        '6379/tcp': [
          {
            HostPort: '0',
          },
        ],
      },
    },
  },
  function (err, data) {
    if (err) {
      return console.error(err);
    }
    console.log(data.StatusCode);
  }
);

/*

function runExec(container) {
  var options = {
    AttachStdout: true,
    AttachStderr: true,
  };

  container.exec(options, function (err, exec) {
    if (err) return;
    exec.start(function (err, stream) {
      if (err) return;

      container.modem.demuxStream(stream, process.stdout, process.stderr);

      exec.inspect(function (err, data) {
        if (err) return;
        console.log(data);
      });
    });
  });
}

docker.createContainer(
  {
    Image: 'meteahaansever/anviserver:latest',
    Tty: true,
  },
  function (err, container) {
    container.start({}, function (err, data) {
      runExec(container);
      console.log(err);
      console.log(data);
    });
  }
);


var docker1 = new Docker(); //defaults to above if env variables are not used
var docker2 = new Docker({ host: 'http://192.168.1.10', port: 3000 });
var docker3 = new Docker({ protocol: 'http', host: '127.0.0.1', port: 3000 });
var docker4 = new Docker({ host: '127.0.0.1', port: 3000 }); //defaults to http
*/
