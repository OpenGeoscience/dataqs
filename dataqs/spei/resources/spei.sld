<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>{name}</sld:Name>
    <sld:UserStyle>
      <sld:Name>{name}</sld:Name>
      <sld:Title>SPEI Drought Index</sld:Title>
      <sld:FeatureTypeStyle>
        <sld:Name>spei03_inv_a1c0d6fd</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ColorMap>
              <sld:ColorMapEntry color="#000000" opacity="0" quantity="-1000.0" label="No Data"/>
              <sld:ColorMapEntry color="#8B1A1A" opacity="1" quantity="-2.33" label="-2.33 or lower"/>
              <sld:ColorMapEntry color="#DE2929" opacity="1" quantity="-1.65" label="-1.65"/>
              <sld:ColorMapEntry color="#F3641D" opacity="1" quantity="-1.28" label="-1.28"/>
              <sld:ColorMapEntry color="#FDC404" opacity="1" quantity="-0.84" label="-0.84"/>
              <sld:ColorMapEntry color="#9AFA94" opacity="1" quantity="0" label="0"/>
              <sld:ColorMapEntry color="#03F2FD" opacity="1" quantity="0.84" label="0.84"/>
              <sld:ColorMapEntry color="#12ADF3" opacity="1" quantity="1.28" label="1.28"/>
              <sld:ColorMapEntry color="#1771DE" opacity="1" quantity="1.65" label="1.65"/>
              <sld:ColorMapEntry color="#00008B" opacity="1" quantity="2.33" label="2.33 or higher"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>