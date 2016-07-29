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
                <sld:ColorMapEntry color="#f7fbff" quantity="0" opacity="1.0" label="0 mm"/>
                <sld:ColorMapEntry color="#e1edf8" quantity="200" opacity="1.0" label="200 mm"/>
                <sld:ColorMapEntry color="#ccdff1" quantity="400" opacity="1.0" label="400 mm"/>
                <sld:ColorMapEntry color="#afd1e7" quantity="600" opacity="1.0" label="600 mm"/>
                <sld:ColorMapEntry color="#88bedc" quantity="800" opacity="1.0" label="800 mm"/>
                <sld:ColorMapEntry color="#5fa6d1" quantity="1000" opacity="1.0" label="1000 mm"/>
                <sld:ColorMapEntry color="#3d8dc3" quantity="1200" opacity="1.0" label="1200 mm"/>
                <sld:ColorMapEntry color="#2171b5" quantity="1400" opacity="1.0" label="1400 mm"/>
                <sld:ColorMapEntry color="#0a539e" quantity="1600" opacity="1.0" label="1600 mm"/>
                <sld:ColorMapEntry color="#08306b" quantity="1800" opacity="1.0" label="1800+ mm"/>
            </sld:ColorMap>
            <sld:ContrastEnhancement/>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
