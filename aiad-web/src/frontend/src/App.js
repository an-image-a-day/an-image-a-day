import React from 'react';

function chunk(array, n) {
  let nChunks = Math.ceil(array.length / n)
  let chunks = []
  for (let i = 0; i < nChunks; ++i) {
    chunks.push(array.slice(i*n, (i+1)*n))
  }
  return chunks
}

class App extends React.Component {
  state = {
    wallpapers: []
  }

  componentDidMount() {
    let base_url = process.env.AIAD_WEB_BACKEND_URL || 'http://localhost:5000';
    fetch(base_url + '/api/v1/wallpapers/channels/General/all')
    .then(res => res.json())
    .then(data => {
      console.log(data)
      this.setState({ wallpapers: data.items })
    })
    .catch(console.log)
  }

  render() {
    let wallpapers = this.state.wallpapers
    return <div style={{padding: '1em'}}>
      <h2>An Image a Day</h2>
      {chunk(wallpapers, 4).map(chunk =>
        <div className="card-deck" style={{paddingBottom: '1em'}}>
          {chunk.map(item => [
            <div className="card" style={{width: "18rem"}}>
              <img class="card-img-top" src={item.wallpaper.resolutions[item.wallpaper.resolutions.length-2].image_url} alt={item.wallpaper.name}/>
              <div className="card-body">
                <h5 className="card-title">{item.date}</h5>
                <p class="card-text">{item.wallpaper.credit.text}</p>
                <a href={item.wallpaper.source_url} className="btn btn-primary">Go to source</a>
              </div>
              <div class="card-footer">
                <small class="text-muted">{item.wallpaper.keywords.join(', ')}</small>
              </div>
            </div>,]
          )}
        </div>
      )}
    </div>
  }
}

export default App;
