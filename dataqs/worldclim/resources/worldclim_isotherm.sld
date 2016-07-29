<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>worldclim_isotherm</sld:Name>
    <sld:UserStyle>
      <sld:Name>worldclim_isotherm</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Geometry>
              <ogc:PropertyName>grid</ogc:PropertyName>
            </sld:Geometry>
            <sld:ColorMap>
              <sld:ColorMapEntry color="#2c7bb6" opacity="1.0" quantity="0" label="0"/>
              <sld:ColorMapEntry color="#61a2cb" opacity="1.0" quantity="10" label="10"/>
              <sld:ColorMapEntry color="#96cae0" opacity="1.0" quantity="25" label="25"/>
              <sld:ColorMapEntry color="#c1e3dd" opacity="1.0" quantity="40" label="40"/>
              <sld:ColorMapEntry color="#e4f3cc" opacity="1.0" quantity="50" label="50"/>
              <sld:ColorMapEntry color="#fef6b5" opacity="1.0" quantity="75" label="75"/>
              <sld:ColorMapEntry color="#fdd48d" opacity="1.0" quantity="85" label="85"/>
              <sld:ColorMapEntry color="#fdb265" opacity="1.0" quantity="90" label="90"/>
              <sld:ColorMapEntry color="#ef7747" opacity="1.0" quantity="95" label="95"/>
              <sld:ColorMapEntry color="#d7191c" opacity="1.0" quantity="100" label="100"/>
            </sld:ColorMap>
            <sld:ContrastEnhancement/>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
