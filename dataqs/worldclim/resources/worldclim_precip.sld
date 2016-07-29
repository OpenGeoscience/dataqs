<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>worldclim_precip</sld:Name>
    <sld:UserStyle>
      <sld:Name>worldclim_precip</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Geometry>
              <ogc:PropertyName>grid</ogc:PropertyName>
            </sld:Geometry>
            <sld:ColorMap>
                <sld:ColorMapEntry color="#f7fbff" quantity="0.000000" opacity="1.0" label="0 mm"/>
                <sld:ColorMapEntry color="#e1edf8" quantity="35" opacity="1.0" label="35 mm"/>
                <sld:ColorMapEntry color="#ccdff1" quantity="70" opacity="1.0" label="70 mm"/>
                <sld:ColorMapEntry color="#afd1e7" quantity="100" opacity="1.0" label="100 mm"/>
                <sld:ColorMapEntry color="#88bedc" quantity="150" opacity="1.0" label="150 mm"/>
                <sld:ColorMapEntry color="#5fa6d1" quantity="180" opacity="1.0" label="180 mm"/>
                <sld:ColorMapEntry color="#3d8dc3" quantity="225" opacity="1.0" label="225 mm"/>
                <sld:ColorMapEntry color="#2171b5" quantity="250" opacity="1.0" label="250 mm"/>
                <sld:ColorMapEntry color="#0a539e" quantity="300" opacity="1.0" label="300 mm"/>
                <sld:ColorMapEntry color="#08306b" quantity="400" opacity="1.0" label="400+ mm"/>
            </sld:ColorMap>
            <sld:ContrastEnhancement/>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
