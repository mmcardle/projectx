import React from 'react';

function CentralContainer(props) {
  return (
    <div className="central-container">
        <div className="central-item">
          {props.children}
        </div>
    </div>
  );
}

export default CentralContainer;
