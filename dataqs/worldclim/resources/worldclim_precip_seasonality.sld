<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>worldclim_precip_seasonality</sld:Name>
    <sld:UserStyle>
      <sld:Name>worldclim_precip_seasonality</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Geometry>
              <ogc:PropertyName>grid</ogc:PropertyName>
            </sld:Geometry>
            <sld:ColorMap>
                <sld:ColorMapEntry color="#f7fbff" quantity="0" opacity="1.0" label="0 mm"/>
                <sld:ColorMapEntry color="#e1edf8" quantity="20" opacity="1.0" label="20"/>
                <sld:ColorMapEntry color="#ccdff1" quantity="40" opacity="1.0" label="40"/>
                <sld:ColorMapEntry color="#afd1e7" quantity="60" opacity="1.0" label="60"/>
                <sld:ColorMapEntry color="#88bedc" quantity="80" opacity="1.0" label="80"/>
                <sld:ColorMapEntry color="#5fa6d1" quantity="100" opacity="1.0" label="100"/>
                <sld:ColorMapEntry color="#3d8dc3" quantity="120" opacity="1.0" label="120"/>
                <sld:ColorMapEntry color="#2171b5" quantity="140" opacity="1.0" label="140"/>
                <sld:ColorMapEntry color="#0a539e" quantity="160" opacity="1.0" label="160"/>
                <sld:ColorMapEntry color="#08306b" quantity="180" opacity="1.0" label="180+"/>
            </sld:ColorMap>
            <sld:ContrastEnhancement/>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
